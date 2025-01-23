class BaseChoice:
    @classmethod
    def choices(cls):
        return [(value, value) for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(value)]

class StoryPlayInstanceState(BaseChoice):
    IN_PROGRESS = 'IN_PROGRESS'
    TERMINATED = 'TERMINATED'



class StoryPlayRecordDataType(BaseChoice):
    AI_GENERATED_TEXT = 'AI_GENERATED_TEXT'
    AUTHORS_TEXT = 'AUTHORS_TEXT'
    AUTHORS_CHOICE_LIST = 'AUTHORS_CHOICE_LIST'
    AUTHORS_INPUT_BOX = 'AUTHORS_INPUT_BOX'
    READERS_ENTERED_TEXT = 'READERS_ENTERED_TEXT'
    READERS_CHOSEN_CHOICE = 'READERS_CHOSEN_CHOICE'
