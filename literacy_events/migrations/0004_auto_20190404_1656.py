# Generated by Django 2.1.7 on 2019-04-04 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prompts', '0006_auto_20190404_1438'),
        ('literacy_events', '0003_auto_20190401_0554'),
    ]

    operations = [
        migrations.AddField(
            model_name='literacyevent',
            name='prompt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='literacy_events', to='prompts.Prompt'),
        ),
        migrations.AlterField(
            model_name='literacyevent',
            name='event_type',
            field=models.CharField(choices=[('0', 'loved story'), ('1', 'commented on story'), ('2', 'forked a story'), ('3', 'published story'), ('3', 'unpublished story'), ('4', 'published book'), ('5', 'added story to book'), ('9', 'removed story from book'), ('6', 'followed'), ('a', 'unfollowed'), ('8', 'signed up')], max_length=1),
        ),
    ]