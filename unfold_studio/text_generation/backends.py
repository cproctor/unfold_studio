# TODO: Instantiate a model for text generation queries. 
# When memoize is True, cache query results.

from openai import OpenAI, APIError
import logging

log = logging.getLogger(__name__)

class TextGenerationBackend:
    """Interface to a text generation service.
    """
    def __init__(self, config):
        self.config = config

    def generate(self, prompt):
        return "GENERATED TEXT"

class OpenAIBackend:
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

    def generate(self, prompt):
        messages = self.get_prompt_context()
        messages.append({
            "role": "user", 
            "content": prompt
        })
        try:
            result = self.api_client.chat.completions.create(
                messages=messages,
                model=self.model, 
                temperature=self.temperature,
            )
            return result.choices[0].message.content
        except APIError as err:
            log.error(f"Error calling OpenAI backend: {err}")
            return "...error generating text..."

text_generation_backends = {
    "OpenAI": OpenAIBackend,
}

def get_text_generation_backend(config):
    """Given a config dict like settings.TEXT_GENERATION,
    instantiates and returns a TextGenerationBackend.
    """
    backend_name = config['backend']
    backend_class = text_generation_backends[backend_name]
    return backend_class(config)

