# Generated by Django 2.1.7 on 2019-04-05 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('literacy_events', '0006_auto_20190405_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='literacyevent',
            name='extra',
            field=models.TextField(blank=True, null=True),
        ),
    ]