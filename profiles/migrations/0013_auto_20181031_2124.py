# Generated by Django 2.1.2 on 2018-10-31 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_auto_20180729_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(choices=[('0', 'loved story'), ('1', 'commented on story'), ('2', 'forked a story'), ('3', 'published story'), ('4', 'published book'), ('5', 'added story to book'), ('9', 'removed story from book'), ('6', 'followed'), ('7', 'you followed'), ('8', 'signed up')], max_length=1),
        ),
    ]
