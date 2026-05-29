from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_add_deprecated_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='tos_updates',
            field=models.BooleanField(default=False),
        ),
    ]
