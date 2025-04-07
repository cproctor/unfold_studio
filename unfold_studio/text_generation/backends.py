# TODO: Instantiate a model for text generation queries. 
# When memoize is True, cache query results.

from openai import OpenAI, APIError
import structlog
from abc import ABC, abstractmethod
import hashlib
import json
from .models import TextGenerationRecord

log = structlog.get_logger("unfold_studio")


class TextGenerationBackendInterface(ABC):
    """Interface to a text generation service.
    """
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def generate(self, prompt):
        pass

    @abstractmethod
    def get_ai_response_by_system_and_user_prompt(self, system_prompt, user_prompt):
        pass

class OpenAIBackend(TextGenerationBackendInterface):
    def __init__(self, config):
        self.config = config
        self.api_client = OpenAI(api_key=config['api_key'])
        self.model = config['model']
        self.temperature = config['temperature']
    
    def _get_messages_hash(self, messages):
        messages_str = json.dumps(messages, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(messages_str.encode()).hexdigest()

    def _get_backend_config_hash(self):
        config_str = json.dumps(self.config, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_str.encode()).hexdigest()

    def _get_cached_response(self, seed, messages_hash, backend_config_hash):
        return TextGenerationRecord.objects.filter(
            seed=seed,
            messages_hash=messages_hash,
            backend_config_hash=backend_config_hash
        ).values_list('result', flat=True).first()

    def _save_to_cache(self, seed, messages_hash, messages, result, backend_config_hash):
        TextGenerationRecord.objects.create(
            seed=seed,
            messages_hash=messages_hash,
            messages=messages,
            result=result,
            backend_config=self.config,
            backend_config_hash=backend_config_hash,
        )

    def _get_messages_for_generate(self, prompt, context_array=None):
        messages = []
        if context_array:
            for context in context_array:
                messages.append({
                    "role": "system",
                    "content": context,
                })

        messages.append({
            "role": "user", 
            "content": prompt
        })

        return messages
    
    def _create_chat_completion(self, messages, seed, hit_cache=True, **extra_api_params):
        messages_hash = self._get_messages_hash(messages)
        backend_config_hash = self._get_backend_config_hash()

        if hit_cache:
            cached_result = self._get_cached_response(seed, messages_hash, backend_config_hash)
            if cached_result:
                return cached_result

        try:
            response = self.api_client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                **extra_api_params
            )
            result = response.choices[0].message.content

            if hit_cache:
                self._save_to_cache(
                    seed=seed,
                    messages_hash=messages_hash,
                    messages=messages,
                    backend_config_hash=backend_config_hash,
                    result=result,
                )
            return result
        except APIError as err:
            log.error("Error calling OpenAI", error=str(err))
            return "...error generating text..."

    def generate(self, prompt, context_array, seed, hit_cache=True):
        messages = self._get_messages_for_generate(prompt, context_array)
        return self._create_chat_completion(
            messages=messages,
            seed=seed,
            hit_cache=hit_cache
        )

    def get_ai_response_by_system_and_user_prompt(self, system_prompt, user_prompt, seed, hit_cache=True):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self._create_chat_completion(
            messages=messages,
            seed=seed,
            hit_cache=hit_cache,
            response_format={"type": "json_object"}
        )
        


class TextGenerationFactory:
    _registry = {
        "OpenAI": OpenAIBackend,
    }

    @classmethod
    def create(cls, config):
        backend_name = config.get('backend')
        if not backend_name:
            raise ValueError("Config must specify a 'backend'")

        backend_class = cls._registry.get(backend_name)
        if not backend_class:
            raise ValueError(f"Unsupported backend: {backend_name}")

        return backend_class(config)
        
        