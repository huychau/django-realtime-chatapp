from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Friend


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'phone', 'bio', 'address')
    search_fields = ('phone', 'user__username')
    list_filter = ('user',)


class FriendAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'message')
    search_fields = ('from_user', 'to_user')


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Friend, FriendAdmin)
