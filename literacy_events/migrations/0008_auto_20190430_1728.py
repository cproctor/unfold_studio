# Generated by Django 2.2 on 2019-04-30 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_events', '0007_literacyevent_extra'),
    ]

    operations = [
        migrations.AlterField(
            model_name='literacyevent',
            name='event_type',
            field=models.CharField(choices=[('0', 'loved story'), ('1', 'commented on story'), ('2', 'forked a story'), ('3', 'published story'), ('3', 'unpublished story'), ('4', 'published book'), ('5', 'added story to book'), ('9', 'removed story from book'), ('6', 'followed'), ('a', 'unfollowed'), ('8', 'signed up'), ('c', 'created prompt'), ('d', 'submitted to prompt'), ('e', 'unsubmitted from prompt'), ('f', 'story knot read'), ('g', 'published prompt as book'), ('h', 'unpublished prompt as book')], max_length=1),
        ),
    ]
