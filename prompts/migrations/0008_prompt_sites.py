# Generated by Django 2.2 on 2019-04-29 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('prompts', '0007_prompt_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
        ),
    ]
