from unfold_studio.models import StoryPlayInstance
from unfold_studio.choices import StoryPlayRecordDataType

class UnfoldStudioService:
    @staticmethod
    def get_story_play_instance(instance_uuid):
        return StoryPlayInstance.objects.get(uuid=instance_uuid)
    
    @staticmethod
    def get_ordered_records(instance):
        return list(instance.records.order_by('story_point'))
    
    @staticmethod
    def is_valid_record_sequence_for_direct_continue(records, start_idx):
        required_types = [
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_CHOICE_LIST,
            StoryPlayRecordDataType.READERS_CHOSEN_CHOICE,
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_TEXT
        ]
        return UnfoldStudioService._check_sequence(records, start_idx, required_types)

    @staticmethod
    def is_valid_record_sequence_for_bridge_and_continue(records, start_idx):
        required_types = [
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_CHOICE_LIST,
            StoryPlayRecordDataType.READERS_CHOSEN_CHOICE,
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_TEXT
        ]
        return UnfoldStudioService._check_sequence(records, start_idx, required_types)

    @staticmethod
    def is_valid_record_sequence_for_needs_input(records, start_idx):
        required_types = [
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_CHOICE_LIST,
            StoryPlayRecordDataType.READERS_CHOSEN_CHOICE,
            StoryPlayRecordDataType.AUTHORS_TEXT
        ]
        return UnfoldStudioService._check_sequence(records, start_idx, required_types)

    @staticmethod
    def is_valid_record_sequence_for_invalid_input(records, start_idx):
        required_types = [
            StoryPlayRecordDataType.AUTHORS_TEXT,
            StoryPlayRecordDataType.AUTHORS_CHOICE_LIST,
            StoryPlayRecordDataType.READERS_CHOSEN_CHOICE,
            StoryPlayRecordDataType.AUTHORS_TEXT
        ]
        return UnfoldStudioService._check_sequence(records, start_idx, required_types)

    @staticmethod
    def _check_sequence(records, start_idx, required_types):
        if start_idx + len(required_types) > len(records):
            return False
            
        for i, required_type in enumerate(required_types):
            if records[start_idx + i].data_type != required_type:
                return False
        return True

    @staticmethod
    def is_authors_text(record):
        return record.data_type == StoryPlayRecordDataType.AUTHORS_TEXT 