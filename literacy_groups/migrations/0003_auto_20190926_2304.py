# Generated by Django 2.2.5 on 2019-09-26 23:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_groups', '0002_auto_20190926_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='literacygroup',
            name='leaders',
            field=models.ManyToManyField(related_name='literacy_groups_leading', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='literacygroup',
            name='members',
            field=models.ManyToManyField(related_name='literacy_groups', to=settings.AUTH_USER_MODEL),
        ),
    ]
