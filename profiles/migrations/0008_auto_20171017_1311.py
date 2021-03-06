# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-17 13:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_auto_20171017_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to='profiles.Profile'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['user', 'timestamp'], name='profiles_ev_user_id_ca3eba_idx'),
        ),
    ]
