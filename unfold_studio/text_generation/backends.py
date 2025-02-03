# TODO: Instantiate a model for text generation queries. 
# When memoize is True, cache query results.

from openai import OpenAI, APIError
import structlog
from abc import ABC, abstractmethod

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
    def get_prompt_context(self):
        pass

    @abstractmethod
    def get_response_for_system_and_user_prompt(self, system_prompt, user_prompt):
        pass

class OpenAIBackend(TextGenerationBackendInterface):
    """Interface to OpenAI API.
    """
    def __init__(self, config):
        self.config = config
        self.api_client = OpenAI(api_key=config['api_key'])
        self.model = config['model']
        self.temperature = config['temperature']

    def get_prompt_context(self):
        """Returns a list of messages which should be prepended to every prompt.
        """
        return []

    def get_messages_for_request(self, prompt, context_array=None):
        messages = self.get_prompt_context()
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

    def generate(self, prompt, context_array):
        messages = self.get_messages_for_request(prompt, context_array)
        try:
            result = self.api_client.chat.completions.create(
                messages=messages,
                model=self.model, 
                temperature=self.temperature,
            )
            return result.choices[0].message.content
        except APIError as err:
            log.error(name="Text Generation Alert", event="Error Calling OpenAI", arg={"error": err})
            return "...error generating text..."
    
    def get_response_for_system_and_user_prompt(self, system_prompt, user_prompt):
        try:
            messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            result = self.api_client.chat.completions.create(
                messages=messages,
                model=self.model, 
                temperature=self.temperature,
            )
            return result.choices[0].message.content
        except APIError as err:
            log.error(name="Text Generation Alert", event="Error Calling OpenAI", arg={"error": err})
            return "...error getting AI direction..."



text_generation_backends = {
    "OpenAI": OpenAIBackend,
}

def get_text_generation_backend(config):
    """Given a config dict like settings.TEXT_GENERATION,
    instantiates and returns a TextGenerationBackendInterface implemented class.
    """
    backend_name = config['backend']
    backend_class = text_generation_backends.get(backend_name)
    if not backend_class:
        raise ValueError(f"Unsupported backend: {backend_name}")
    return backend_class(config)

