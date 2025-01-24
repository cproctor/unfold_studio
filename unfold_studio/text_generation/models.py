from django.db import models

# Create your models here.


class TextGenerationRecord(models.Model):
    seed = models.PositiveIntegerField()
    hashed_key = models.CharField(max_length=64)
    prompt = models.TextField()
    context = models.JSONField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    backend_name = models.CharField(max_length=64)
