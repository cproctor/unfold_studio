from django.db import migrations


class Migration(migrations.Migration):
    """Merge point: both branches altered submitted_story_version on promptstory."""

    dependencies = [
        ('prompts', '0013_softdelete_mixin'),
        ('prompts', '0013_alter_promptstory_submitted_story_version'),
    ]

    operations = []
