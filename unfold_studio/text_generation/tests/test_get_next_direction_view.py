import pytest
from unittest.mock import Mock, patch
from django.http import JsonResponse
from text_generation.views import GetNextDirectionView
from text_generation.constants import StoryContinueDirections
import json

@pytest.fixture
def valid_request_data():
    return {
        'user_input': 'Test input',
        'target_knot_data': {'knotContents': ['Content 1', 'Content 2']},
        'story_play_instance_uuid': 'test-uuid',
        'ai_seed': 42
    }

@pytest.fixture
def mock_story_history():
    return {
        'timeline': [
            {'role': 'system', 'content': 'System message 1'},
            {'role': 'user', 'content': 'User message 1'}
        ]
    }

@pytest.fixture
def mock_ai_response():
    return {
        'probabilities': {
            'DIRECT_CONTINUE': 0.6,
            'BRIDGE_AND_CONTINUE': 0.2,
            'NEEDS_INPUT': 0.1,
            'INVALID_USER_INPUT': 0.1
        },
        'direct_continue': {
            'next_knot': 'next_knot_1'
        },
        'bridge_and_continue': {
            'bridge_text': 'Bridge text',
            'next_knot': 'next_knot_2'
        },
        'needs_input': {
            'guidance_text': 'What would you like to do next?',
            'reason': 'User input needed'
        },
        'invalid_user_input': {
            'guidance_text': 'Invalid input, please try again',
            'reason': 'Invalid user input'
        }
    }

class TestGetNextDirectionView:
    def test_validate_request_with_valid_data(self, valid_request_data):
        view = GetNextDirectionView()
        is_valid, error = view.validate_request(valid_request_data)
        assert is_valid
        assert error is None

    def test_validate_request_with_missing_fields(self):
        view = GetNextDirectionView()
        invalid_data = {'user_input': 'Test input'}
        is_valid, error = view.validate_request(invalid_data)
        assert not is_valid
        assert 'Missing required field' in error

    def test_build_system_and_user_prompt(self, valid_request_data, mock_story_history):
        view = GetNextDirectionView()
        system_prompt, user_prompt = view.build_system_and_user_prompt(
            valid_request_data['target_knot_data'],
            mock_story_history,
            valid_request_data['user_input']
        )
        assert system_prompt is not None
        assert user_prompt is not None
        assert valid_request_data['user_input'] in user_prompt
        assert json.dumps(mock_story_history, indent=2) in user_prompt

    def test_parse_and_validate_ai_response_with_valid_data(self, mock_ai_response):
        view = GetNextDirectionView()
        response = json.dumps(mock_ai_response)
        parsed_data = view.parse_and_validate_ai_response(response)
        assert parsed_data == mock_ai_response

    def test_parse_and_validate_ai_response_with_invalid_json(self):
        view = GetNextDirectionView()
        with pytest.raises(json.JSONDecodeError):
            view.parse_and_validate_ai_response('invalid json')

    def test_parse_and_validate_ai_response_with_missing_probabilities(self):
        view = GetNextDirectionView()
        invalid_response = {
            'probabilities': {
                'DIRECT_CONTINUE': 0.6,
                'BRIDGE_AND_CONTINUE': 0.2
                # Missing other required directions
            }
        }
        with pytest.raises(ValueError, match='Missing probability for'):
            view.parse_and_validate_ai_response(json.dumps(invalid_response))

    def test_parse_and_validate_ai_response_with_invalid_probability_sum(self):
        view = GetNextDirectionView()
        invalid_response = {
            'probabilities': {
                'DIRECT_CONTINUE': 1.0,
                'BRIDGE_AND_CONTINUE': 0.5,
                'NEEDS_INPUT': 0.3,
                'INVALID_USER_INPUT': 0.2
            }
        }
        with pytest.raises(ValueError, match='Total probability does not equal 1'):
            view.parse_and_validate_ai_response(json.dumps(invalid_response))

    def test_determine_next_direction_details_from_ai_response(self, mock_ai_response):
        view = GetNextDirectionView()
        direction, content = view.determine_next_direction_details_from_ai_response(mock_ai_response)
        assert direction == 'DIRECT_CONTINUE'  # Highest probability
        assert content == mock_ai_response['direct_continue']

    @patch('text_generation.views.UnfoldStudioService')
    @patch('text_generation.views.TextGenerationFactory')
    def test_get_next_direction_details_for_story_success(
        self, mock_factory, mock_unfold_service, valid_request_data, mock_story_history, mock_ai_response
    ):
        view = GetNextDirectionView()
        mock_unfold_service.get_story_play_history.return_value = mock_story_history
        
        mock_backend = Mock()
        mock_backend.get_ai_response_by_system_and_user_prompt.return_value = json.dumps(mock_ai_response)
        mock_factory.create.return_value = mock_backend

        direction, content = view.get_next_direction_details_for_story(
            valid_request_data['target_knot_data'],
            mock_story_history,
            valid_request_data['user_input'],
            valid_request_data['ai_seed']
        )
        
        assert direction == 'DIRECT_CONTINUE'
        assert content == mock_ai_response['direct_continue']
        mock_backend.get_ai_response_by_system_and_user_prompt.assert_called_once()

    @patch('text_generation.views.UnfoldStudioService')
    @patch('text_generation.views.TextGenerationFactory')
    def test_get_next_direction_details_for_story_error(
        self, mock_factory, mock_unfold_service, valid_request_data, mock_story_history
    ):
        view = GetNextDirectionView()
        mock_unfold_service.get_story_play_history.return_value = mock_story_history
        
        mock_backend = Mock()
        mock_backend.get_ai_response_by_system_and_user_prompt.side_effect = Exception('API Error')
        mock_factory.create.return_value = mock_backend

        direction, content = view.get_next_direction_details_for_story(
            valid_request_data['target_knot_data'],
            mock_story_history,
            valid_request_data['user_input'],
            valid_request_data['ai_seed']
        )
        
        assert direction == StoryContinueDirections.NEEDS_INPUT
        assert content['guidance_text'] == 'What would you like to do next?'
        assert content['reason'] == 'System failure'

    @patch('text_generation.views.StoryTransitionRecord')
    def test_save_story_transition_record(self, mock_story_transition_record, valid_request_data):
        view = GetNextDirectionView()
        previous_timeline = {'timeline': ['entry1', 'entry2']}
        ai_decision = {'direction': 'DIRECT_CONTINUE', 'content': {'next_knot': 'knot1'}}
        
        view.save_story_transition_record(
            valid_request_data['story_play_instance_uuid'],
            previous_timeline,
            valid_request_data['target_knot_data'],
            valid_request_data['user_input'],
            ai_decision
        )
        
        mock_story_transition_record.objects.create.assert_called_once_with(
            story_play_instance_uuid=valid_request_data['story_play_instance_uuid'],
            previous_story_timeline=previous_timeline,
            target_knot_data=valid_request_data['target_knot_data'],
            user_input=valid_request_data['user_input'],
            ai_decision=ai_decision
        )

    @patch('text_generation.views.UnfoldStudioService')
    @patch('text_generation.views.TextGenerationFactory')
    @patch('text_generation.views.StoryTransitionRecord')
    def test_post_success(
        self, mock_story_transition_record, mock_factory, mock_unfold_service,
        valid_request_data, mock_story_history, mock_ai_response
    ):
        view = GetNextDirectionView()
        mock_unfold_service.get_story_play_history.return_value = mock_story_history
        
        mock_backend = Mock()
        mock_backend.get_ai_response_by_system_and_user_prompt.return_value = json.dumps(mock_ai_response)
        mock_factory.create.return_value = mock_backend

        request = Mock()
        request.body = json.dumps(valid_request_data).encode()

        response = view.post(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 200
        result = json.loads(response.content)['result']
        assert result['direction'] == 'DIRECT_CONTINUE'
        assert result['content'] == mock_ai_response['direct_continue']

    def test_post_invalid_json(self):
        view = GetNextDirectionView()
        request = Mock()
        request.body = b'invalid json'

        response = view.post(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 400
        assert 'Invalid JSON in request body' in response.content.decode()

    def test_post_missing_required_fields(self):
        view = GetNextDirectionView()
        request = Mock()
        request.body = json.dumps({'user_input': 'test'}).encode()

        response = view.post(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 400
        assert 'Missing required field' in response.content.decode() 