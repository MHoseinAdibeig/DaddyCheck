from django.contrib import admin
from django.urls import path, include

from .tools import group_task_progress_bar


urlpatterns = [
    path("api/Auth/", include("src.core.urls")),
    path("api/Centers/", include("src.centers.urls")),
    path("api/Analysis/", include("src.analysis.urls")),
    path("backup/", include("src.core.urls")),
    path("backup/", include("src.centers.urls")),
    path("backup/", include("src.analysis.urls")),
    path("admin/", admin.site.urls),
    path(
        "admin/tools/progress_bar/<str:group_id>/<int:should_update_version>/<int:sync>",
        group_task_progress_bar,
    ),
    # path("admin/tools/terminator/<str:group_id>", terminate_task),
]
