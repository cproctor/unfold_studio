# Generated by Django 2.1.7 on 2019-03-31 21:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('unfold_studio', '0002_auto_20160401_2103'),
        ('prompts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LiteracyEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('event_type', models.CharField(choices=[('0', 'loved story'), ('1', 'commented on story'), ('2', 'forked a story'), ('3', 'published story'), ('4', 'published book'), ('5', 'added story to book'), ('9', 'removed story from book'), ('6', 'followed'), ('a', 'unfollowed'), ('8', 'signed up')], max_length=1)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='literacy_events', to='unfold_studio.Book')),
                ('object_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='literacy_events_as_object', to=settings.AUTH_USER_MODEL)),
                ('story', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='literacy_events', to='unfold_studio.Story')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='literacy_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='literacy_events.LiteracyEvent')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='literacyevent',
            index=models.Index(fields=['subject', 'timestamp'], name='literacy_ev_subject_88c1f8_idx'),
        ),
    ]
