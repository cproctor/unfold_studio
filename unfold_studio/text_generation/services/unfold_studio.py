from unfold_studio.models import StoryPlayInstance, Story
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, When, Value, CharField
import json

class UnfoldStudioService:

    @staticmethod
    def get_story_play_history(story_play_instance_uuid):
        try:
            story_play_instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)
            return json.loads(story_play_instance.get_history())
        except StoryPlayInstance.DoesNotExist:
            raise ValueError(f"Story play instance {story_play_instance_uuid} not found")

    @staticmethod
    def get_story_id_from_play_instance_uuid(story_play_instance_uuid):
        try:
            story_play_instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)
            return story_play_instance.story.id
        except StoryPlayInstance.DoesNotExist:
            raise ValueError(f"Story play instance {story_play_instance_uuid} not found")

    @staticmethod
    def get_knot_data(story_id, target_knot_name):
        try:
            story = Story.objects.get(id=story_id)
            knot_data = story.get_knot_data(target_knot_name)
            if not knot_data:
                raise ValueError(f"Knot '{target_knot_name}' not found in story")
            return knot_data
        except Story.DoesNotExist:
            raise ValueError(f"Story with id {story_id} not found")
        except Exception as e:
            raise ValueError(f"Error getting knot data: {str(e)}")


