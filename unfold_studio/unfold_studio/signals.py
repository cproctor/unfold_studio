from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from unfold_studio.models import Story

@receiver(post_save, sender=Story)
def update_search_vector(sender, instance, **kwargs):
    # Session-owned anonymous drafts must not be discoverable via full-text search.
    if instance.author_id is None and not instance.public and not instance.shared:
        Story.objects.filter(pk=instance.pk).update(search=None)
        return
    Story.objects.filter(pk=instance.pk).update(search=SearchVector('title', 'ink'))
