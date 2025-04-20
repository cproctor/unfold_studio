import sys
from unittest.mock import Mock, patch
import pytest
from generated_text_evaluator.flows.generate_triplets_flow import GenerateTripletsFlow
from generated_text_evaluator.constants import TripletType

@pytest.fixture(autouse=True, scope="session")
def init_mock_story_play_record_data_type():
    global mock_story_play_record_data_type
    mock_story_play_record_data_type = Mock()
    mock_story_play_record_data_type.AUTHORS_TEXT = "AUTHORS_TEXT"
    mock_story_play_record_data_type.AUTHORS_CHOICE_LIST = "AUTHORS_CHOICE_LIST"
    mock_story_play_record_data_type.READERS_CHOSEN_CHOICE = "READERS_CHOSEN_CHOICE"

@pytest.fixture
def mock_records():
    records = []
    
    # Knot 1
    record0 = Mock()
    record0.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record0.data = {'text': 'Initial knot text'}
    record0.id = 0
    records.append(record0)

    record1 = Mock()
    record1.data_type = mock_story_play_record_data_type.AUTHORS_CHOICE_LIST
    record1.data = {'text': 'First choice list'}
    record1.id = 1
    records.append(record1)

    record2 = Mock()
    record2.data_type = mock_story_play_record_data_type.READERS_CHOSEN_CHOICE
    record2.data = {'text': 'First chosen choice'}
    record2.id = 2
    records.append(record2)

    record3 = Mock()
    record3.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record3.data = {'text': 'First chosen choice'}
    record3.id = 3
    records.append(record3)

    # Knot 2
    record4 = Mock()
    record4.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record4.data = {'text': 'Second knot text'}
    record4.id = 4
    records.append(record4)

    record4b = Mock()
    record4b.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record4b.data = {'text': 'Second knot text 2'}
    record4b.id = 5
    records.append(record4b)

    record5 = Mock()
    record5.data_type = mock_story_play_record_data_type.AUTHORS_CHOICE_LIST
    record5.data = {'text': 'Second choice list'}
    record5.id = 6
    records.append(record5)

    record6 = Mock()
    record6.data_type = mock_story_play_record_data_type.READERS_CHOSEN_CHOICE
    record6.data = {'text': 'Second chosen choice'}
    record6.id = 7
    records.append(record6)

    record7 = Mock()
    record7.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record7.data = {'text': 'Second chosen choice'}
    record7.id = 8
    records.append(record7)

    # Knot 3
    record8 = Mock()
    record8.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record8.data = {'text': 'Third knot text'}
    record8.id = 9
    records.append(record8)

    record9 = Mock()
    record9.data_type = mock_story_play_record_data_type.AUTHORS_CHOICE_LIST
    record9.data = {'text': 'Third choice list'}
    record9.id = 10
    records.append(record9)

    record10 = Mock()
    record10.data_type = mock_story_play_record_data_type.READERS_CHOSEN_CHOICE
    record10.data = {'text': 'Third chosen choice'}
    record10.id = 11
    records.append(record10)

    record11 = Mock()
    record11.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record11.data = {'text': 'Third chosen choice'}
    record11.id = 12
    records.append(record11)

    # Final Knot
    record12 = Mock()
    record12.data_type = mock_story_play_record_data_type.AUTHORS_TEXT
    record12.data = {'text': 'Ending knot text'}
    record12.id = 13
    records.append(record12)

    return records

class TestGenerateTripletsFlow:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.flow = GenerateTripletsFlow()

    def test_get_direct_continue_triplets(self, mock_records):
        triplets = self.flow.get_direct_continue_triplets(mock_records)
        
        assert len(triplets) == 3
        assert isinstance(triplets[0], dict)
        assert triplets[0]['triplet_type'] == TripletType.DIRECT_CONTINUE
        assert triplets[0]['initial_text'] == 'Initial knot text'
        assert triplets[0]['chosen_choice'] == {'text': 'First chosen choice'}
        assert triplets[0]['next_text'] == 'Second knot text'
        
        assert triplets[1]['initial_text'] == 'Second knot text 2'
        assert triplets[1]['chosen_choice'] == {'text': 'Second chosen choice'}
        assert triplets[1]['next_text'] == 'Third knot text'
        
        assert triplets[2]['initial_text'] == 'Third knot text'
        assert triplets[2]['chosen_choice'] == {'text': 'Third chosen choice'}
        assert triplets[2]['next_text'] == 'Ending knot text'

    def test_get_bridge_and_continue_triplets(self, mock_records):
        triplets = self.flow.get_bridge_and_continue_triplets(mock_records)
        
        assert len(triplets) == 1
        assert isinstance(triplets[0], dict)
        assert triplets[0]['triplet_type'] == TripletType.BRIDGE_AND_CONTINUE
        assert triplets[0]['initial_text'] == 'Initial knot text'
        assert triplets[0]['chosen_choice'] == {'text': 'First chosen choice'}
        assert triplets[0]['next_text'] == 'Second knot text 2'

    def test_get_needs_input_triplets(self, mock_records):
        self.flow.needs_input_range = 1
        self.flow.needs_input_difference_threshold = 1
        
        triplets = self.flow.get_needs_input_triplets(mock_records)
        
        assert len(triplets) == 1
        assert isinstance(triplets[0], dict)
        assert triplets[0]['triplet_type'] == TripletType.NEEDS_INPUT
        assert triplets[0]['initial_text'] == 'Initial knot text'
        assert triplets[0]['chosen_choice'] == {'text': 'First chosen choice'}
        assert triplets[0]['next_text'] == 'Second knot text 2'

    def test_get_invalid_user_input_triplets(self, mock_records):
        # Set thresholds to 0 for simpler testing
        self.flow.invalid_input_range = 1
        self.flow.invalid_input_difference_threshold = 1
        self.flow.invalid_input_max_attempts_per_triplet = 1
        
        # Mock the random action and matching score
        self.flow.generate_random_action = lambda: 'Random action'
        self.flow.calculate_matching_score = lambda initial_text, chosen_choice, next_text: 0.1
        
        triplets = self.flow.get_invalid_user_input_triplets(mock_records)
        
        assert len(triplets) == 1
        assert isinstance(triplets[0], dict)
        assert triplets[0]['triplet_type'] == TripletType.INVALID_USER_INPUT
        assert triplets[0]['initial_text'] == 'Initial knot text'
        assert triplets[0]['chosen_choice'] == 'Random action'
        assert triplets[0]['next_text'] == 'Second knot text 2'
        assert triplets[0]['matching_score'] == 0.1

    def test_generate_random_action(self):
        action = self.flow.generate_random_action()
        assert isinstance(action, str)
        assert len(action) > 0

    def test_calculate_matching_score(self):
        initial_text = "Test initial text"
        chosen_choice = "Test choice"
        next_text = "Test next text"
        score = self.flow.calculate_matching_score(initial_text, chosen_choice, next_text)
        assert isinstance(score, float)
        assert 0 <= score <= 1 