import io

from django.contrib import admin
from django.http import JsonResponse
from django.conf import settings
from django.urls import path

from rest_framework.parsers import JSONParser


from .models import User, Device, Message, MessageLevel, Key

from src.bucket import Bucket
from src import tools


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "level", "code", "message_en", "message_fa", "status_code")
    # list_editable = ("status_code",)
    fields = ("level", "code", "message_en", "message_fa", "status_code")
    list_filter = ("level__title",)
    list_per_page = 10
    ordering = ("id",)
    search_fields = ("id", "code", "message_en", "message_fa")

    change_list_template = settings.PROJECT_ROOT + "/core/templates/messages_list.html"



@admin.register(MessageLevel)
class MessageLevelAdmin(admin.ModelAdmin):
    # TODO add form

    change_list_template = (
        settings.PROJECT_ROOT + "/core/templates/messagelevels_list.html"
    )



@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ("filename", "last_modified")
    # list_filter = ("level__title",)
    list_per_page = 30
    ordering = ("filename",)
    search_fields = ("filename", "last_modified")

    change_list_template = settings.PROJECT_ROOT + "/core/templates/keys_list.html"




admin.site.register(User)
admin.site.register(Device)
