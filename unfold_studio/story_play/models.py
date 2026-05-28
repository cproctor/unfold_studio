from django.db import models
from django.contrib.auth.models import User
from django.db.models import Case, When, Value, CharField
import uuid
import json
from django.core.serializers.json import DjangoJSONEncoder
from story_play.choices import StoryPlayInstanceState, StoryPlayRecordDataType


class StoryPlayInstance(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='story_play_instances')
    story = models.ForeignKey('unfold_studio.Story', on_delete=models.CASCADE, related_name='story_play_instances')
    state = models.CharField(max_length=32, choices=StoryPlayInstanceState.choices(), default=StoryPlayInstanceState.IN_PROGRESS)

    def get_history(self):
        records = self.records.annotate(
            record_type=Case(
                When(data_type='AUTHORS_TEXT', then=Value('narrative')),
                When(data_type='AI_GENERATED_TEXT', then=Value('narrative')),
                When(data_type='AUTHORS_CHOICE_LIST', then=Value('offered_choices')),
                When(data_type='READERS_CHOSEN_CHOICE', then=Value('chosen_choice')),
                When(data_type='AUTHORS_INPUT_BOX', then=Value('input_prompt')),
                When(data_type='AUTHORS_CONTINUE_INPUT_BOX', then=Value('input_prompt')),
                When(data_type='READERS_ENTERED_TEXT', then=Value('user_input')),
                When(data_type='READERS_CONTINUE_ENTERED_TEXT', then=Value('user_input')),
                default=Value('other'),
                output_field=CharField()
            )
        ).order_by('story_point')

        return self._format_history(records)

    def _format_history(self, records):
        history = {'timeline': []}
        for record in records:
            history['timeline'].append({
                'type': record.record_type,
                'content': record.data,
            })
        return json.dumps(history, cls=DjangoJSONEncoder)

    def __str__(self):
        return f"StoryPlayInstance {self.uuid} - id: {self.id}"

    class Meta:
        app_label = 'unfold_studio'


class StoryPlayRecord(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    story_play_instance = models.ForeignKey(StoryPlayInstance, on_delete=models.CASCADE, related_name='records')
    story_point = models.IntegerField()
    data_type = models.CharField(max_length=30, choices=StoryPlayRecordDataType.choices())
    data = models.JSONField()

    class Meta:
        app_label = 'unfold_studio'
        ordering = ['story_point']

    def __str__(self):
        return f"StoryPlayRecord {self.uuid} - id: {self.id}"
