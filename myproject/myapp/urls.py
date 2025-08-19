from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),        # Home page → HTML
    path('users/', views.alluser, name='users'),  # Users page → message
    path('prescription/', views.prescription, name='prescription'),
    path("login/", views.login_view, name="login"),
    path('register/', views.register, name="register"),
]
