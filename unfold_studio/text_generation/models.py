from django.db import models

# Create your models here.


class TextGenerationRecord(models.Model):
    seed = models.PositiveIntegerField()
    hashed_key = models.CharField(max_length=64)  # Hash of prompt + context
    prompt = models.TextField()  # Store raw prompt for ledgering
    context = models.JSONField()  # Store context as JSON
    result = models.TextField()  # Store the AI-generated result
    created_at = models.DateTimeField(auto_now_add=True)
    backend_name = models.CharField(max_length=64)

    class Meta:
        unique_together = ('seed', 'hashed_key') 