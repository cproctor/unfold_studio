from django.db import migrations


class Migration(migrations.Migration):
    """Merge point: both branches removed anyone_can_join and created JoinCode."""

    dependencies = [
        ('literacy_groups', '0005_softdelete_mixin'),
        ('literacy_groups', '0005_remove_literacygroup_anyone_can_join_joincode'),
    ]

    operations = []
