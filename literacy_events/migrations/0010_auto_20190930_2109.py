# Generated by Django 2.2.5 on 2019-09-30 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_groups', '0004_literacygroup_deleted'),
        ('literacy_events', '0009_auto_20190506_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='literacyevent',
            name='literacy_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='literacy_events', to='literacy_groups.LiteracyGroup'),
        ),
        migrations.AlterField(
            model_name='literacyevent',
            name='event_type',
            field=models.CharField(choices=[('0', 'loved story'), ('1', 'commented on story'), ('2', 'forked a story'), ('3', 'published story'), ('3', 'unpublished story'), ('4', 'published book'), ('5', 'added story to book'), ('9', 'removed story from book'), ('6', 'followed'), ('a', 'unfollowed'), ('8', 'signed up'), ('c', 'created prompt'), ('d', 'submitted to prompt'), ('e', 'unsubmitted from prompt'), ('f', 'story knot read'), ('g', 'published prompt as book'), ('h', 'unpublished prompt as book'), ('i', 'tagged a story version'), ('j', 'joined literacy group'), ('k', 'left literacy group')], max_length=1),
        ),
    ]