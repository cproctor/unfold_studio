from unfold_studio.models import Story, Book
from django.contrib import admin
from reversion.admin import VersionAdmin
from django.db.models import Count

@admin.register(Story)
class StoryAdmin(VersionAdmin):
    list_display = [
        'id',
        'title',
        'author',
        'edit_date',
        'shared',
        'public'
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

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title', 
        'owner',
    ]
    list_display_links = [
        'title'
    ]
    list_select_related = [
        'owner'
    ]
    readonly_fields = [
        'stories',
    ]
