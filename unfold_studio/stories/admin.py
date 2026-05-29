from stories.models import Story
from django.contrib import admin
from reversion.admin import VersionAdmin


class NoCommentVersionAdmin(VersionAdmin):
    "Subclass of VersionAdmin which doesn't pollute the revision comments."
    def log_addition(self, request, object, change_message=None):
        admin.ModelAdmin.log_addition(request, object, change_message)

    def log_change(self, request, object, message):
        super().log_change(request, object, '')


@admin.register(Story)
class StoryAdmin(NoCommentVersionAdmin):
    list_display = [
        'id',
        'title',
        'author',
        'edit_date',
        'shared'
    ]
    list_display_links = [
        'title'
    ]
    list_select_related = [
        'author'
    ]
    exclude = [
        'includes',
    ]
    readonly_fields = [
        'parent',
        'loves',
    ]
