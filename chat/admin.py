from django.contrib import admin
from .models import Room, Message


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'user',)
    search_fields = ('name', 'user__username')
    list_filter = ('user',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'message', 'user', 'room')
    search_fields = ('message', 'subject', 'user__username')
    list_filter = ('user', 'room',)


admin.site.register(Room, RoomAdmin)
admin.site.register(Message, MessageAdmin)
