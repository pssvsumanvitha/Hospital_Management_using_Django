from django.urls import path
from myapp import views

# No app_name/namespace here — keeping URL names global so all existing
# {% url 'name' %} tags in templates work without any prefix changes.

urlpatterns = [
    path('',                                views.home_view,             name='home'),
    path('register/',                       views.register_view,         name='register'),
    path('login/',                          views.login_view,            name='login'),
    path('logout/',                         views.logout_view,           name='logout'),
    path('appointment/',                    views.appointment_view,      name='appointment'),
    path('prescription/',                   views.prescription_view,     name='prescription'),
    path('prescription/download/<int:pk>/', views.download_prescription, name='download_prescription'),
    path('dashboard/',                      views.admin_dashboard,       name='dashboard'),
]