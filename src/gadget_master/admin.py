import secrets
import qrcode
import os
from ecdsa import SigningKey, VerifyingKey

from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.http import JsonResponse

# from django.shortcuts import render
from src import tools

from .models import GadgetInfo, DeviceModel
from .forms import GadgetForm, DeviceForm


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "zoom_level",
    )
    form = DeviceForm

    change_list_template = (
        settings.PROJECT_ROOT + "/gadget_master/templates/devicemodels_list.html"
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("export/json/", self.export_json),
        ]
        return my_urls + urls

    def export_json(self, request, _queryset=None):
        data = tools.admin_export_json(DeviceModel)
        return JsonResponse(data, safe=False)


@admin.register(GadgetInfo)
class GadgetInfoAdmin(admin.ModelAdmin):
    add_form_template = (
        settings.PROJECT_ROOT + "/gadget_master/templates/add_gadget.htm"
    )
    change_form_template = (
        settings.PROJECT_ROOT + "/gadget_master/templates/detail_gadget.htm"
    )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                os.remove(obj.imgpath)
            except Exception:
                pass
        return super().delete_queryset(request, queryset)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["gadget"] = self.get_object(request, unquote(object_id))
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        # pylint: disable-msg=too-many-locals


        extra_context["form"] = form
        return super().add_view(request, form_url=form_url, extra_context=extra_context)
