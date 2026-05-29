import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView

from story_play.models import StoryPlayInstance, StoryPlayRecord
from stories.models import Story


class CreateStoryPlayInstanceView(CreateView):

    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body)
        story_id = request_body['story_id']

        # Story must be publicly playable; record authenticated user if present.
        story = get_object_or_404(Story, pk=story_id)
        if not story.shared:
            return JsonResponse({"error": "Story is not available for play"}, status=403)

        user = request.user if request.user.is_authenticated else None
        story_play_instance = StoryPlayInstance.objects.create(
            user=user,
            story=story
        )

        return JsonResponse({"story_play_instance_uuid": str(story_play_instance.uuid)})


class CreateStoryPlayRecordView(CreateView):

    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body)

        story_play_instance_uuid = request_body['story_play_instance_uuid']
        data_type = request_body['data_type']
        data = request_body['data']
        story_point = request_body['story_point']

        story_play_instance = get_object_or_404(StoryPlayInstance, uuid=story_play_instance_uuid)

        story_play_record = StoryPlayRecord.objects.create(
            story_play_instance=story_play_instance,
            data_type=data_type,
            data=data,
            story_point=story_point,
        )

        return JsonResponse({"story_play_record_uuid": str(story_play_record.uuid)})
