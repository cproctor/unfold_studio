# Generated by Django 2.1.7 on 2019-03-31 22:06

from django.db import migrations
from django.db.models import F
from datetime import timedelta

def create_literacy_events(apps, schema_editor):
    """
    Converts old-style Events into LiteracyEvents. Previously, we had a messy model trying to 
    keep multiple Events for each thing that happened, one owned by each user. We want a 1-to-1 
    relationship between things that happen and LiteracyEvents. Most of the time, we can get a 
    normalized form of the event by selecting where user==subject. The only exception is following, 
    which relies on some complexity to encode two users.

    Once LiteracyEvents are created, we create one Notification for every old Event. We match the
    corresponding LiteracyEvent by timestamp because at the time of this migration, there were
    no types of events which were created simultaneously.
    """
    FOLLOWED = '6' # Model property not available in migration

    OldEvent = apps.get_model('profiles', 'Event')
    LiteracyEvent = apps.get_model('literacy_events', 'LiteracyEvent')
    Notification = apps.get_model('literacy_events', 'Notification')
    for e in OldEvent.objects.filter(user=F('subject')).all():
        LiteracyEvent(
            timestamp = e.timestamp,
            event_type = e.event_type, 
            subject = e.subject, 
            book = e.book,
            story = e.story,
            object_user = None
        ).save()
    for e in OldEvent.objects.filter(event_type=FOLLOWED).all():
        LiteracyEvent(
            timestamp = e.timestamp,
            event_type = e.event_type, 
            subject = e.subject, 
            book = None,
            story = None,
            object_user = e.user
        ).save()

    for le in LiteracyEvent.objects.all():
        for e in OldEvent.objects.filter(
            subject=le.subject,
            event_type=le.event_type, 
            story=le.story,
            book=le.book
        ).all():
            Notification(recipient=e.user, event=le, seen=True).save()

    for le in LiteracyEvent.objects.filter(event_type=FOLLOWED).all():
        Notification(recipient=le.subject, event=le, seen=True).save()
        Notification(recipient=le.object_user, event=le, seen=True).save()

    print("{} old events, {} new events, {} notifications".format(
        OldEvent.objects.count(), LiteracyEvent.objects.count(), Notification.objects.count()
    ))

def drop_literacy_events(apps, schema_editor):
    "Deletes all LitearcyEvents and Notifications"
    LiteracyEvent = apps.get_model('literacy_events', 'LiteracyEvent')
    Notification = apps.get_model('literacy_events', 'Notification')
    for e in LiteracyEvent.objects.iterator():
        e.delete()
    for n in Notification.objects.iterator():
        n.delete()

class Migration(migrations.Migration):
    """
    A data migration to assist with migrating from the old profiles.models.Event. Populates
    this model with unique versions of each profiles.models.Event.
    """

    dependencies = [
        ('literacy_events', '0001_initial'),
        ('profiles', '0013_auto_20181031_2124'),
    ]

    operations = [
        migrations.RunPython(create_literacy_events, drop_literacy_events)
    ]
