# Generated by Django 2.2.5 on 2019-09-26 18:44

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('literacy_groups', '0001_initial'),
        ('prompts', '0008_prompt_sites'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prompt',
            name='assignee_groups',
        ),
        migrations.RemoveField(
            model_name='prompt',
            name='owners',
        ),
        migrations.RemoveField(
            model_name='prompt',
            name='sites',
        ),
        migrations.AddField(
            model_name='prompt',
            name='literacy_group',
            field=models.ForeignKey(null=True, on_delete='cascade', related_name='prompts', to='literacy_groups.LiteracyGroup'),
        ),
    ]