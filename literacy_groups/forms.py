from django.forms import ModelForm
from literacy_groups.models import LiteracyGroup

class LiteracyGroupForm(ModelForm):
    model = LiteracyGroup
    fields = ['name', 'accepting_new_members']
