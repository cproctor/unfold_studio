# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-24 01:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unfold_studio', '0014_auto_20171018_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]