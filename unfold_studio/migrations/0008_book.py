# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-16 17:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('unfold_studio', '0007_story_featured'),
    ]

    operations = [
        # Book creation moved to 0002
    ]
