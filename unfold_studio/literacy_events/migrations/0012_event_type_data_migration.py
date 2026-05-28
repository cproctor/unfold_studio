from django.db import migrations

EVENT_TYPE_MAP = {
    '0': 'loved_story',
    '1': 'commented',
    '2': 'forked',
    '3': 'published_story',
    'b': 'unpublished_story',
    '4': 'published_book',
    '5': 'added_to_book',
    '9': 'removed_from_book',
    '6': 'followed',
    'a': 'unfollowed',
    '8': 'signed_up',
    'c': 'created_prompt',
    'd': 'submitted_to_prompt',
    'e': 'removed_from_prompt',
    'f': 'read_story',
    'g': 'published_as_book',
    'h': 'unpublished_book',
    'i': 'tagged_version',
    'j': 'joined_group',
    'k': 'left_group',
}


def migrate_event_types(apps, schema_editor):
    LiteracyEvent = apps.get_model('literacy_events', 'LiteracyEvent')
    for old_value, new_value in EVENT_TYPE_MAP.items():
        LiteracyEvent.objects.filter(event_type=old_value).update(event_type=new_value)


def reverse_event_types(apps, schema_editor):
    LiteracyEvent = apps.get_model('literacy_events', 'LiteracyEvent')
    for old_value, new_value in EVENT_TYPE_MAP.items():
        LiteracyEvent.objects.filter(event_type=new_value).update(event_type=old_value)


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_events', '0011_event_type_textchoices_and_user_fk_null'),
    ]

    operations = [
        migrations.RunPython(migrate_event_types, reverse_code=reverse_event_types),
    ]
