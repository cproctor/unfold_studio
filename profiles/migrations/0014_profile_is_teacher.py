# Generated by Django 2.2.5 on 2019-09-27 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_auto_20181031_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_teacher',
            field=models.BooleanField(default=False),
        ),
    ]