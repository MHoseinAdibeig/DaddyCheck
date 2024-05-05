from django.urls import path
from . import views

urlpatterns = [
    path("gadgets/", views.Gadgets.as_view(), name="analysis_gadgets"),
    path("state/", views.AnalysisState.as_view(), name="analysis_state"),
    path("qc/", views.VideoQC.as_view(), name="analysis_qc"),
    path("create/", views.AnalysisBegin.as_view(), name="analysis_create"),
    path("discard/", views.AnalysisDiscard.as_view(), name="analysis_discard"),
    path("run/", views.Analyse.as_view(), name="analysis_run"),
    path("results/", views.Results.as_view(), name="analysis_results"),

]
