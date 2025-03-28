import json
from unittest.mock import patch, Mock
import pytest
from django.test import RequestFactory
from text_generation.views import GenerateTextView

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def generate_text_view():
    return GenerateTextView()

@patch('text_generation.views.TextGenerationFactory')
def test_generate_text_success(mock_factory, request_factory, generate_text_view):
    mock_backend = Mock()
    mock_backend.generate.return_value = "Generated text"
    mock_factory.create.return_value = mock_backend

    request_data = {
        "prompt": "Test prompt",
        "context_array": ["Context 1", "Context 2"],
        "ai_seed": 123
    }

    request = request_factory.post(
        '/generate',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    response = generate_text_view.post(request)
    response_data = json.loads(response.content)

    assert response.status_code == 200
    assert response_data == {"result": "Generated text"}


def test_generate_text_missing_prompt(request_factory, generate_text_view):
    request_data = {
        "context_array": ["Context 1", "Context 2"],
        "ai_seed": 123
    }

    request = request_factory.post(
        '/generate',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    response = generate_text_view.post(request)
    response_data = json.loads(response.content)

    assert response.status_code == 400
    assert response_data == {"error": "Prompt cannot be empty"}


def test_generate_text_invalid_json(request_factory, generate_text_view):
    request = request_factory.post(
        '/generate',
        data="invalid json",
        content_type='application/json'
    )

    response = generate_text_view.post(request)
    response_data = json.loads(response.content)

    assert response.status_code == 400
    assert response_data == {"error": "Invalid JSON in request body."}


@patch('text_generation.views.TextGenerationFactory')
def test_generate_text_backend_error(mock_factory, request_factory, generate_text_view):
    mock_backend = Mock()
    mock_backend.generate.side_effect = Exception("Backend error")
    mock_factory.create.return_value = mock_backend

    request_data = {
        "prompt": "Test prompt",
        "context_array": ["Context 1", "Context 2"],
        "ai_seed": 123
    }

    request = request_factory.post(
        '/generate',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    response = generate_text_view.post(request)
    response_data = json.loads(response.content)

    assert response.status_code == 500
    assert response_data == {"error": "Backend error"} 
