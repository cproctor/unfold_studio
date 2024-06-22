from profiles.models import Profile
from django.contrib import admin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = [
        "user__username"
    ]
    readonly_fields = [
        "user",
        "following",
    ]

