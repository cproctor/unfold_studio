from django.db import models

# Create your models here.


class TextGenerationRecord(models.Model):
    seed = models.PositiveIntegerField()
    prompt = models.TextField()
    context = models.JSONField()
    hashed_key = models.CharField(max_length=64)
    result = models.TextField()
    backend_config = models.JSONField()
    backend_config_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
