from django.contrib import admin
from django.contrib.auth import get_user_model

from user.models import UserFollowing


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "profile_image",
        "phone_number",
    )


@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "following_user_id",
    )
