from django.contrib import admin
from comments.models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'author',
        'story',
        'creation_date',
        'message',
        'deleted'
    ]
    readonly_fields = ("author", "story")
    
