import secrets
from django.db import models
from django.contrib.auth.models import User


class APIKey(models.Model):
    key = models.CharField(max_length=40, unique=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        super().save(*args, **kwargs)

    def rotate(self):
        self.key = secrets.token_hex(20)
        self.save(update_fields=['key'])

    def __str__(self):
        return f"APIKey for {self.owner.username} ({'revoked' if self.revoked else 'active'})"

    class Meta:
        verbose_name = "API Key"
