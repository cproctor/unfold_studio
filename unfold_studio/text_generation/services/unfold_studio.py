from unfold_studio.models import StoryPlayInstance
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, When, Value, CharField
import json

class UnfoldStudioService:

    @staticmethod
    def get_story_play_history(story_play_instance_uuid):
        story_play_instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)
        return json.loads(story_play_instance.get_history())

