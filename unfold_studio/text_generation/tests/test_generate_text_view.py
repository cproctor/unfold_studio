import json
from unittest.mock import patch, Mock
import pytest
from django.test import RequestFactory
from text_generation.views import GenerateTextView

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def valid_request_data():
    return {
        "prompt": "Test prompt",
        "context_array": ["Context 1", "Context 2"],
        "ai_seed": 123
    }

class TestGenerateTextView:
    @pytest.fixture(autouse=True)
    def setup(self, request_factory):
        self.view = GenerateTextView()
        self.factory = request_factory

    def _create_request(self, data):
        return self.factory.post(
            '/generate',
            data=json.dumps(data) if isinstance(data, dict) else data,
            content_type='application/json'
        )

    @patch('text_generation.views.TextGenerationFactory')
    def test_generate_text_success(self, mock_factory, valid_request_data):
        mock_backend = Mock()
        mock_backend.generate.return_value = "Generated text"
        mock_factory.create.return_value = mock_backend

        request = self._create_request(valid_request_data)
        response = self.view.post(request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data == {"result": "Generated text"}
        mock_backend.generate.assert_called_once_with(
            prompt=valid_request_data["prompt"],
            context_array=valid_request_data["context_array"],
            seed=valid_request_data["ai_seed"],
            hit_cache=True
        )

    def test_generate_text_missing_prompt(self):
        invalid_data = {
            "context_array": ["Context 1", "Context 2"],
            "ai_seed": 123
        }
        request = self._create_request(invalid_data)

        response = self.view.post(request)
        response_data = json.loads(response.content)

        assert response.status_code == 400
        assert response_data == {"error": "Prompt cannot be empty"}

    def test_generate_text_invalid_json(self):
        request = self._create_request("invalid json")

        response = self.view.post(request)
        response_data = json.loads(response.content)

        assert response.status_code == 400
        assert response_data == {"error": "Invalid JSON in request body."}

    @patch('text_generation.views.TextGenerationFactory')
    def test_generate_text_backend_error(self, mock_factory, valid_request_data):
        mock_backend = Mock()
        mock_backend.generate.side_effect = Exception("Backend error")
        mock_factory.create.return_value = mock_backend

        request = self._create_request(valid_request_data)
        response = self.view.post(request)
        response_data = json.loads(response.content)

        assert response.status_code == 500
        assert response_data == {"error": "Backend error"}
        