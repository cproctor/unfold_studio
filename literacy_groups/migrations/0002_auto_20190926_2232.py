# Generated by Django 2.2.5 on 2019-09-26 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_groups', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='literacygroup',
            old_name='accepting_new_members',
            new_name='anyone_can_join',
        ),
        migrations.RemoveField(
            model_name='literacygroup',
            name='password',
        ),
        migrations.RemoveField(
            model_name='literacygroup',
            name='password_required',
        ),
        migrations.AddField(
            model_name='literacygroup',
            name='join_code',
            field=models.TextField(default='xxxxxx'),
            preserve_default=False,
        ),
    ]
