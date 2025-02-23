from django.db import models


class TextGenerationRecord(models.Model):
    seed = models.PositiveIntegerField()
    prompt = models.TextField()
    context = models.JSONField()
    hashed_key = models.CharField(max_length=64)
    result = models.TextField()
    backend_config = models.JSONField()
    backend_config_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)


class ContinueDecisionRecord(models.Model):
    story_play_instance_uuid = models.UUIDField()
    previous_story_timeline = models.JSONField()
    target_knot_data = models.JSONField()
    user_input = models.CharField(max_length=256)
    ai_decision = models.JSONField()
    # ai_evaluation = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)