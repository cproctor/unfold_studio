# Generated by Django 2.1.2 on 2018-10-22 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unfold_studio', '0026_auto_20181022_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='json',
            field=models.TextField(blank=True, null=True),
        ),
    ]