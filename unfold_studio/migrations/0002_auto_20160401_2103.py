# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 21:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('unfold_studio', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='creation_date',
        ),
        migrations.RemoveField(
            model_name='story',
            name='edit_date',
        ),
        migrations.RemoveField(
            model_name='story',
            name='view_count',
        ),
    ]
