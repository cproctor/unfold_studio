from books.models import Book
from django.contrib import admin


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
