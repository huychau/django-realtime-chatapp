from django.contrib import admin
from .models import Room, Participant, Message


admin.site.register(Room)
admin.site.register(Participant)
admin.site.register(Message)
