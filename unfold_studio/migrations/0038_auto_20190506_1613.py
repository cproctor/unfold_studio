# Generated by Django 2.2 on 2019-05-06 16:13

from django.db import migrations
from reversion.models import Version, Revision
from django.utils import timezone

def update_revision_comments(apps, schema_editor):
    #Revision = apps.get_model('reversion', 'Revision')
    #Version = apps.get_model('reversion', 'Version')
    Story = apps.get_model('unfold_studio', 'Story')

    for r in Revision.objects.iterator():
        r.comment = ''
        if timezone.is_naive(r.date_created):
            r.date_created = timezone.make_aware(r.date_created)
        r.save()

    for s in Story.objects.iterator():
        versions = Version.objects.get_for_object(s)
        if versions.exists():
            r = versions.last().revision
            if s.parent:
                if s.parent.author:
                    r.comment = "{} forked from @story:{} by @user:{}".format(s.title, s.parent.id, 
                            s.parent.author.id)
                else:
                    r.comment = "{} forked from @story:{}".format(s.title, s.parent.id)
            else:
                r.comment = "Initial version of @story:{}".format(s.id)
            r.save()

def reverse_update(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('unfold_studio', '0037_auto_20190430_2247'),
        ('comments', '0002_auto_20190506_2050'),
    ]

    operations = [
        migrations.RunPython(update_revision_comments, reverse_update)
    ]
