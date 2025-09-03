from django.urls import path
from . import views

app_name = 'employee_portal'

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
]
