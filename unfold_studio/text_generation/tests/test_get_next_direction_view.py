import pytest
from unittest.mock import Mock, patch
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from text_generation.views import GetNextDirectionView
from text_generation.constants import StoryContinueDirections
import json

@pytest.fixture
def valid_request_data():
    return {
        'user_input': 'Test input',
        'target_knot_name': 'test_knot',
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
def mock_knot_data():
    return {
        'knotContents': ['Content 1', 'Content 2'],
        'knotChoices': ['Choice 1', 'Choice 2']
    }

@pytest.fixture
def mock_decision():
    return {'choice': 'DIRECT_CONTINUE', 'confidence': 0.9, 'probabilities': []}

def make_backend(decision_choice='DIRECT_CONTINUE', text='Generated text'):
    backend = Mock()
    backend.get_choice_decision.return_value = {'choice': decision_choice, 'confidence': 0.9, 'probabilities': []}
    backend.is_decision_cached.return_value = True
    backend.get_ai_response_by_system_and_user_prompt.return_value = text
    return backend

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

    def test_build_decision_input(self, valid_request_data, mock_story_history, mock_knot_data):
        view = GetNextDirectionView()
        decision_input = view.build_decision_input(
            mock_knot_data, mock_story_history, valid_request_data['user_input']
        )
        assert valid_request_data['user_input'] in decision_input
        assert json.dumps(mock_story_history, indent=2) in decision_input

    def test_direct_continue_uses_only_decision_model(self, mock_story_history, mock_knot_data):
        backend = make_backend('DIRECT_CONTINUE')
        with patch('text_generation.views.get_llm_backend', return_value=backend):
            direction, content = GetNextDirectionView().get_next_direction_details_for_story(
                mock_knot_data, mock_story_history, 'Test input', 42
            )
        assert direction == 'DIRECT_CONTINUE'
        assert 'reason' in content
        backend.get_choice_decision.assert_called_once()
        backend.get_ai_response_by_system_and_user_prompt.assert_not_called()

    def test_invalid_input_uses_only_decision_model(self, mock_story_history, mock_knot_data):
        backend = make_backend('INVALID_USER_INPUT')
        with patch('text_generation.views.get_llm_backend', return_value=backend):
            direction, content = GetNextDirectionView().get_next_direction_details_for_story(
                mock_knot_data, mock_story_history, 'ung', 42
            )
        assert direction == 'INVALID_USER_INPUT'
        backend.get_ai_response_by_system_and_user_prompt.assert_not_called()

    def test_bridge_generates_bridge_text(self, mock_story_history, mock_knot_data):
        backend = make_backend('BRIDGE_AND_CONTINUE', 'A bridge. ')
        with patch('text_generation.views.get_llm_backend', return_value=backend):
            direction, content = GetNextDirectionView().get_next_direction_details_for_story(
                mock_knot_data, mock_story_history, 'Test input', 42
            )
        assert direction == 'BRIDGE_AND_CONTINUE'
        assert content['bridge_text'] == 'A bridge.'
        backend.get_ai_response_by_system_and_user_prompt.assert_called_once()
        user_prompt = backend.get_ai_response_by_system_and_user_prompt.call_args[0][1]
        assert 'BRIDGE_AND_CONTINUE' in user_prompt

    def test_needs_input_generates_guidance_text(self, mock_story_history, mock_knot_data):
        backend = make_backend('NEEDS_INPUT', 'Look around.')
        with patch('text_generation.views.get_llm_backend', return_value=backend):
            direction, content = GetNextDirectionView().get_next_direction_details_for_story(
                mock_knot_data, mock_story_history, 'Test input', 42
            )
        assert direction == 'NEEDS_INPUT'
        assert content['guidance_text'] == 'Look around.'

    def test_decision_error_falls_back_to_needs_input(self, mock_story_history, mock_knot_data):
        backend = make_backend()
        backend.get_choice_decision.side_effect = Exception('API Error')
        with patch('text_generation.views.get_llm_backend', return_value=backend):
            direction, content = GetNextDirectionView().get_next_direction_details_for_story(
                mock_knot_data, mock_story_history, 'Test input', 42
            )
        assert direction == StoryContinueDirections.NEEDS_INPUT
        assert content['guidance_text'] == 'What would you like to do next?'
        assert content['reason'] == 'System failure'

    def test_unknown_choice_falls_back_to_needs_input(self, mock_story_history, mock_knot_data):
        backend = make_backend('SOMETHING_ELSE')
        with patch('text_generation.views.get_llm_backend', return_value=backend):
            direction, content = GetNextDirectionView().get_next_direction_details_for_story(
                mock_knot_data, mock_story_history, 'Test input', 42
            )
        assert direction == StoryContinueDirections.NEEDS_INPUT
        assert content['reason'] == 'System failure'

    @patch('text_generation.views.StoryTransitionRecord')
    def test_save_story_transition_record(self, mock_story_transition_record, valid_request_data, mock_knot_data):
        view = GetNextDirectionView()
        previous_timeline = {'timeline': ['entry1', 'entry2']}
        ai_decision = {'direction': 'DIRECT_CONTINUE', 'content': {'next_knot': 'knot1'}}
        
        view.save_story_transition_record(
            valid_request_data['story_play_instance_uuid'],
            previous_timeline,
            mock_knot_data,
            valid_request_data['user_input'],
            ai_decision
        )
        
        mock_story_transition_record.objects.create.assert_called_once_with(
            story_play_instance_uuid=valid_request_data['story_play_instance_uuid'],
            previous_story_timeline=previous_timeline,
            target_knot_data=mock_knot_data,
            user_input=valid_request_data['user_input'],
            ai_decision=ai_decision
        )

    @patch('text_generation.views.UnfoldStudioService')
    @patch('text_generation.views.StoryTransitionRecord')
    def test_post_success(
        self, mock_story_transition_record, mock_unfold_service,
        valid_request_data, mock_story_history, mock_knot_data
    ):
        view = GetNextDirectionView()
        mock_unfold_service.get_story_play_history.return_value = mock_story_history
        mock_unfold_service.get_story_id_from_play_instance_uuid.return_value = 1
        mock_unfold_service.get_knot_data.return_value = mock_knot_data
        
        request = Mock()
        request.body = json.dumps(valid_request_data).encode()

        with patch('text_generation.views.get_llm_backend', return_value=make_backend('DIRECT_CONTINUE')):
            response = view.post(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 200
        result = json.loads(response.content)['result']
        assert result['direction'] == 'DIRECT_CONTINUE'
        assert 'reason' in result['content']

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

    def test_dispatch_requires_authentication(self, valid_request_data):
        factory = RequestFactory()
        request = factory.post(
            '/get_next_direction',
            data=json.dumps(valid_request_data),
            content_type='application/json',
        )
        request.user = AnonymousUser()
        response = GetNextDirectionView.as_view()(request)
        assert response.status_code == 401

    @pytest.mark.django_db
    def test_dispatch_allows_authenticated_user(
        self, valid_request_data, mock_story_history, mock_knot_data,
    ):
        user = User.objects.create_user("continueuser", "c@example.com", "password123")
        factory = RequestFactory()
        request = factory.post(
            '/get_next_direction',
            data=json.dumps(valid_request_data),
            content_type='application/json',
        )
        request.user = user
        with patch('text_generation.views.UnfoldStudioService') as mock_unfold_service, \
                patch('text_generation.views.get_llm_backend', return_value=make_backend()), \
                patch('text_generation.views.StoryTransitionRecord'):
            mock_unfold_service.get_story_play_history.return_value = mock_story_history
            mock_unfold_service.get_story_id_from_play_instance_uuid.return_value = 1
            mock_unfold_service.get_knot_data.return_value = mock_knot_data
            response = GetNextDirectionView.as_view()(request)
        assert response.status_code == 200
