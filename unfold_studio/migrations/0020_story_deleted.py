# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-08 17:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unfold_studio', '0019_auto_20171027_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
