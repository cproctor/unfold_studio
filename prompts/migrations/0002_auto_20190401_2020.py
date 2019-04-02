# Generated by Django 2.1.7 on 2019-04-01 20:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('prompts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prompt',
            options={'ordering': ['-due_date']},
        ),
        migrations.AddField(
            model_name='prompt',
            name='creation_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='prompt',
            name='due_date',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]