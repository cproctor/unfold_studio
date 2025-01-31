from unfold_studio.models import StoryPlayInstance
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, When, Value, CharField
import json

class UnfoldStudioService:

    @staticmethod
    def get_story_play_history(story_play_instance_uuid):
        story_play_instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)
        # Get all records ordered by story_point
        records = story_play_instance.records.annotate(
            record_type=Case(
                When(data_type='AUTHORS_TEXT', then=Value('narrative')),
                When(data_type='AUTHORS_CHOICE_LIST', then=Value('offered_choices')),
                When(data_type='READERS_CHOSEN_CHOICE', then=Value('chosen_choice')),
                When(data_type='AUTHORS_INPUT_BOX', then=Value('input_prompt')),
                When(data_type='READERS_ENTERED_TEXT', then=Value('user_input')),
                When(data_type='AI_GENERATED_TEXT', then=Value('narrative')),
                When(data_type='AUTHORS_CONTINUE_INPUT_BOX', then=Value('input_prompt')),
                When(data_type='READERS_CONTINUE_ENTERED_TEXT', then=Value('user_input')),
                default=Value('other'),
                output_field=CharField()
            )
        ).order_by('story_point')

        history = {
            'timeline': []
        }

        current_choices = []
        for record in records:
            entry = {
                'type': record.record_type,
                'content': record.data,
            }

            history['timeline'].append(entry)

        return json.dumps(history, cls=DjangoJSONEncoder)
