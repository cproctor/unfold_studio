# Generated by Django 2.1.7 on 2019-04-01 16:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('unfold_studio', '0002_auto_20160401_2103'),
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
        ('auth', '0009_alter_user_last_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('assignee_groups', models.ManyToManyField(blank=True, related_name='prompts_assigned', to='auth.Group')),
                ('owners', models.ManyToManyField(related_name='prompts_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PromptStory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prompts.Prompt')),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unfold_studio.Story')),
                ('submitted_story_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reversion.Version')),
            ],
        ),
        migrations.AddField(
            model_name='prompt',
            name='submissions',
            field=models.ManyToManyField(related_name='prompts_submitted', through='prompts.PromptStory', to='unfold_studio.Story'),
        ),
    ]
