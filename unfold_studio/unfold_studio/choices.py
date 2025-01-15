class BaseChoice:
    @classmethod
    def choices(cls):
        return [(value, value) for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(value)]

class StoryPlayInstanceState(BaseChoice):
    IN_PROGRESS = 'IN_PROGRESS'
    TERMINATED = 'TERMINATED'



class StoryPlayRecordDataType(BaseChoice):
    AI_GENERATED_TEXT = 'AI_GENERATED_TEXT'
    READER_CHOSEN_CHOICE = 'READER_CHOSEN_CHOICE'

    CHOICES = [
        (AI_GENERATED_TEXT, 'AI_GENERATED_TEXT'),
        (READER_CHOSEN_CHOICE, 'READER_CHOSEN_CHOICE'),
    ]
