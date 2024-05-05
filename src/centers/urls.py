from django.urls import path
from . import views

urlpatterns = [
    path("centers/", views.Centers.as_view(), name="centers_centers"),
    path("categories/", views.Categories.as_view(), name="centers_categories"),
    path("cities/", views.Cities.as_view(), name="centers_cities"),
]
