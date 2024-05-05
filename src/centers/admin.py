from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q

from .models import Center, Category, City
from .forms import CenterForm
from src import tools

endpoint = settings.CDN_ENDPOINT


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    form = CenterForm

    list_per_page = 10
    list_max_show_all = 2000
    ordering = ("id",)
    search_fields = ("title",)
    list_display = (
        "id",
        "category",
        "title",
        "short_name",
        "city",
        "phone",
        "loc_latitude",
        "loc_longitude",
    )
    list_editable = (
        # NOTE Adding list editable would cause buttons to disappear
        # "category",
        # # "short_name",
    )
    list_filter = (
        "category",
        "city",
    )

    change_list_template = (
        settings.PROJECT_ROOT + "/centers/templates/centers_list.html"
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("upload/logos/", self.upload_logos,),
            path("upload/maps/", self.upload_maps,),
            path("download/logos/", self.download_logos,),
            path("download/maps/", self.download_maps,),
            path("export/json/", self.export_json),
        ]
        return my_urls + urls



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "short_name",
        "title",
    )
    change_list_template = (
        settings.PROJECT_ROOT + "/centers/templates/categories_list.html"
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("upload/logos/", self.upload_logos,),
            path("download/logos/", self.download_logos,),
            path("export/json/", self.export_json),
        ]
        return my_urls + urls

    def upload_logos(self, request, _queryset=None):
        queryset = Category.objects.filter(~Q(short_name=None))
        data = tools.admin_upload_logo(queryset)
        return JsonResponse(data)

    def download_logos(self, request, _queryset=None):
        queryset = Category.objects.filter(~Q(short_name=None))
        data = tools.admin_download_logo(queryset)
        return JsonResponse(data)

    def export_json(self, request, _queryset=None):
        data = tools.admin_export_json(Category)
        return JsonResponse(data)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_per_page = 10
