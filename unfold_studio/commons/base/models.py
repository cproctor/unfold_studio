from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class SoftDeleteMixin(models.Model):
    """
    Adds soft-delete behaviour to a model. Calling .delete() marks the record
    deleted rather than removing it. The default manager (objects) filters out
    deleted records; use all_objects to see everything.

    Any custom manager on a model inheriting SoftDeleteMixin must itself inherit
    from SoftDeleteManager so the deleted=False filter is not lost.
    """
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted", "deleted_at"])

    def restore(self):
        self.deleted = False
        self.deleted_at = None
        self.save(update_fields=["deleted", "deleted_at"])

    class Meta:
        abstract = True
