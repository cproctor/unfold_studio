# Generated by Django 2.2.5 on 2019-09-27 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_groups', '0003_auto_20190926_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='literacygroup',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]