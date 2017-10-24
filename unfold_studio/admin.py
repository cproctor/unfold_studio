from unfold_studio.models import Story, Book
from django.contrib import admin
from reversion.admin import VersionAdmin

@admin.register(Story)
class StoryAdmin(VersionAdmin):
    pass

admin.site.register(Book)
