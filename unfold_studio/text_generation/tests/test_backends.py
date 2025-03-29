import pytest
from unittest.mock import Mock, patch
from text_generation.backends import TextGenerationFactory, OpenAIBackend
from openai import APIError

@pytest.fixture
def openai_config():
    return {
        'backend': 'OpenAI',
        'api_key': 'test-key',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.7,
    }

@pytest.fixture
def mock_openai_response():
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Generated text"))]
    return mock_response

class TestTextGenerationFactory:
    def test_create_with_valid_backend(self, openai_config):
        backend = TextGenerationFactory.create(openai_config)
        assert isinstance(backend, OpenAIBackend)
        assert backend.config == openai_config

    def test_create_with_missing_backend(self):
        config = {'api_key': 'test-key'}
        with pytest.raises(ValueError, match="Config must specify a 'backend'"):
            TextGenerationFactory.create(config)

    def test_create_with_invalid_backend(self):
        config = {'backend': 'InvalidBackend', 'api_key': 'test-key'}
        with pytest.raises(ValueError, match="Unsupported backend: InvalidBackend"):
            TextGenerationFactory.create(config)

class TestOpenAIBackend:
    def test_initialization(self, openai_config):
        backend = OpenAIBackend(openai_config)
        assert backend.config == openai_config
        assert backend.model == openai_config['model']
        assert backend.temperature == openai_config['temperature']

    def test_get_messages_for_generate_without_context(self, openai_config):
        backend = OpenAIBackend(openai_config)
        messages = backend._get_messages_for_generate("Test prompt")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Test prompt"

    def test_get_messages_for_generate_with_context(self, openai_config):
        backend = OpenAIBackend(openai_config)
        context_array = ["Context 1", "Context 2"]
        messages = backend._get_messages_for_generate("Test prompt", context_array)
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Context 1"
        assert messages[1]["role"] == "system"
        assert messages[1]["content"] == "Context 2"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "Test prompt"

    def test_get_messages_hash(self, openai_config):
        backend = OpenAIBackend(openai_config)
        messages = [{"role": "user", "content": "Test"}]
        hash1 = backend._get_messages_hash(messages)
        hash2 = backend._get_messages_hash(messages)
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64

    def test_get_backend_config_hash(self, openai_config):
        backend = OpenAIBackend(openai_config)
        hash1 = backend._get_backend_config_hash()
        hash2 = backend._get_backend_config_hash()
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64

    @patch('text_generation.backends.OpenAI')
    @patch('text_generation.backends.TextGenerationRecord.objects')
    def test_generate_success(self, mock_objects, mock_openai, openai_config, mock_openai_response):
        mock_objects.filter.return_value.values_list.return_value.first.return_value = None
        mock_objects.create.return_value = None
        
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        backend = OpenAIBackend(openai_config)
        
        result = backend.generate("Test prompt", [], 42)
        
        assert result == "Generated text"
        mock_openai.return_value.chat.completions.create.assert_called_once()
        mock_objects.create.assert_called_once()

    @patch('text_generation.backends.OpenAI')
    @patch('text_generation.backends.TextGenerationRecord.objects')
    def test_generate_with_context(self, mock_objects, mock_openai, openai_config, mock_openai_response):
        mock_objects.filter.return_value.values_list.return_value.first.return_value = None
        mock_objects.create.return_value = None
        
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        backend = OpenAIBackend(openai_config)
        
        result = backend.generate("Test prompt", ["Context"], 42)
        
        assert result == "Generated text"
        call_args = mock_openai.return_value.chat.completions.create.call_args[1]
        assert len(call_args['messages']) == 2
        assert call_args['messages'][0]["role"] == "system"
        assert call_args['messages'][0]["content"] == "Context"

    @patch('text_generation.backends.OpenAI')
    @patch('text_generation.backends.TextGenerationRecord.objects')
    def test_generate_api_error(self, mock_objects, mock_openai, openai_config):
        mock_objects.filter.return_value.values_list.return_value.first.return_value = None
        mock_objects.create.return_value = None
    
        mock_request = Mock()
        mock_body = {"error": {"message": "API Error"}}
        mock_openai.return_value.chat.completions.create.side_effect = APIError("API Error", request=mock_request, body=mock_body)
        backend = OpenAIBackend(openai_config)
        
        result = backend.generate("Test prompt", [], 42)
        
        assert result == "...error generating text..."

    @patch.object(OpenAIBackend, '_create_chat_completion')
    def test_get_ai_response_by_system_and_user_prompt(self, mock_create, openai_config):
        backend = OpenAIBackend(openai_config)
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is the weather?"
        
        mock_create.return_value = '{"weather": "sunny"}'
        result = backend.get_ai_response_by_system_and_user_prompt(
            system_prompt, user_prompt, 42
        )
        
        assert result == '{"weather": "sunny"}'
        mock_create.assert_called_once_with(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            seed=42,
            hit_cache=True,
            response_format={"type": "json_object"}
        )

    @patch('text_generation.backends.TextGenerationRecord.objects')
    @patch('text_generation.backends.OpenAI')
    def test_cache_hit(self, mock_openai, mock_objects, openai_config):
        mock_objects.filter.return_value.values_list.return_value.first.return_value = "Cached text"
        backend = OpenAIBackend(openai_config)
        
        result = backend.generate("Test prompt", [], 42)
        
        assert result == "Cached text"
        mock_objects.filter.assert_called_once()
        mock_openai.return_value.chat.completions.create.assert_not_called()

    @patch('text_generation.backends.TextGenerationRecord.objects')
    @patch('text_generation.backends.OpenAI')
    def test_cache_miss(self, mock_openai, mock_objects, openai_config):
        mock_objects.filter.return_value.values_list.return_value.first.return_value = None
        mock_objects.create.return_value = None
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="New text"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        backend = OpenAIBackend(openai_config)
        result = backend.generate("Test prompt", [], 42)
        
        assert result == "New text"
        mock_objects.create.assert_called_once()
        mock_openai.return_value.chat.completions.create.assert_called_once()

    @patch('text_generation.backends.TextGenerationRecord.objects')
    @patch('text_generation.backends.OpenAI')
    def test_generate_with_hit_cache_false(self, mock_openai, mock_objects, openai_config):
        mock_filter = Mock()
        mock_values_list = Mock()
        mock_first = Mock()
        
        mock_objects.filter.return_value = mock_values_list
        mock_values_list.values_list.return_value = mock_first
        mock_first.first.return_value = "Cached text"
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="New text"))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        backend = OpenAIBackend(openai_config)
        result = backend.generate("Test prompt", [], 42, hit_cache=False)
        
        assert result == "New text"
        mock_objects.filter.assert_not_called()
        mock_openai.return_value.chat.completions.create.assert_called_once()
        mock_objects.create.assert_not_called()

    @patch('text_generation.backends.TextGenerationRecord.objects')
    @patch('text_generation.backends.OpenAI')
    def test_generate_with_hit_cache_true(self, mock_openai, mock_objects, openai_config):
        mock_objects.filter.return_value.values_list.return_value.first.return_value = "Cached text"
        
        backend = OpenAIBackend(openai_config)
        result = backend.generate("Test prompt", [], 42, hit_cache=True)
        
        assert result == "Cached text"
        mock_objects.filter.assert_called_once()
        mock_openai.return_value.chat.completions.create.assert_not_called()
        mock_objects.create.assert_not_called()