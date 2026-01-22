from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("appointment/", views.book_appointment, name="appointment"),
    path("prescription/", views.prescription, name="prescription"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
