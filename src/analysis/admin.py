from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html

from .models import State, Analysis, Result, SampleDetail, Gadget

from src import tools

# Register your models here.


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "message",
        "is_new_analysis_permitted",
    )
    list_filter = ("is_new_analysis_permitted",)

    change_list_template = (
        settings.PROJECT_ROOT + "/analysis/templates/states_list.html"
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("export/json/", self.export_json),
        ]
        return my_urls + urls

    def export_json(self, request, _queryset=None):
        data = tools.admin_export_json(State)
        return JsonResponse(data)


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
        "user",
        "state",
        "register_date",
        "ip",
        "analyse_col",
        "upload_files_col",
    )

    change_list_template = (
        settings.PROJECT_ROOT + "/analysis/templates/analysis_list.html"
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("analyse/<str:analysis_id>/", self.analyse),
            path("upload_files/<str:analysis_id>/", self.upload_files),
        ]
        return my_urls + urls

    def analyse(self, request, analysis_id):
        analysis = Analysis.objects.get(id=analysis_id)
        data = analysis.analyse()
        return JsonResponse(data)

    def upload_files(self, request, analysis_id):
        analysis = Analysis.objects.get(id=analysis_id)
        data = analysis.upload_files()
        return JsonResponse(data)

    def analyse_col(self, obj):
        return format_html(
            """
                <a class="button daddy-green" onclick="analyse('{pk}')">
                    Analyse
                </a>
            """,
            pk=str(obj.pk),
        )

    analyse_col.short_description = "Run Analysis"

    def upload_files_col(self, obj):
        return format_html(
            """
                <a class="button daddy-green" onclick="upload_files('{pk}')">
                    Upload Files
                </a>
            """,
            pk=str(obj.pk),
        )

    upload_files_col.short_description = "Upload Files"


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = ("__str__", "prog", "nprog", "immotile", "quantity", "status_col")
    # list_filter = ("level__title",)
    list_per_page = 30
    # ordering = ("",)
    search_fields = (
        "analysis__id",
        "analysis__title",
    )

    def status_col(self, obj):  # TODO This method should be developed further
        return format_html(
            '<div style="width:100%%; height:100%%; background-color:orange;">{}</div>',
            obj.__str__(),
        )

    status_col.short_description = "Status"


admin.site.register(SampleDetail)
admin.site.register(Gadget)
