# Generated by Django 2.2 on 2019-04-29 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('unfold_studio', '0035_auto_20190411_1553'),
        ('prompts', '0006_auto_20190404_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prompts', to='unfold_studio.Book'),
        ),
    ]
