# Generated by Django 2.1.7 on 2019-04-04 14:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('prompts', '0005_prompt_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prompt',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
