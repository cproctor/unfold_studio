from django.contrib import admin
from research.models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['owner', 'created_at', 'last_used_at', 'revoked']
    list_filter = ['revoked']
    readonly_fields = ['key', 'created_at', 'last_used_at']
    list_select_related = ['owner']
