from django.forms import ModelForm
from literacy_groups.models import LiteracyGroup

class LiteracyGroupForm(ModelForm):
    model = LiteracyGroup
    fields = ['name', 'anyone_can_join']
