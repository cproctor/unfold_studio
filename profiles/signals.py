from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles.models import Profile
from literacy_events.models import LiteracyEvent, Notification

@receiver(post_save, sender=User, dispatch_uid="literacy_event_notification")
def user_signed_up_events(sender, **kwargs):
    "When a user signs up, create a profile and a literacy event"
    user = kwargs['instance']
    if kwargs['created']:
        Profile.objects.create(user=user)
        LiteracyEvent.objects.create(
            subject=user,
            event_type=LiteracyEvent.SIGNED_UP,
        )
