from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.Signup.as_view(), name="core_signup"),
    path("signup/anonymous/", views.SignupAnonymous.as_view(), name="core_signup_anon"),
    path("signup/confirm/", views.SignupConfirm.as_view(), name="core_signup_confirm"),
    path("login/", views.Login.as_view(), name="core_login"),
    path("logout/", views.Logout.as_view(), name="core_logout"),


]
