from django.urls import path
from . import views

app_name = 'employee_portal'

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('api/fetch-notifications/', views.fetch_notifications, name='fetch_notifications'),
       # URL that the clock-in form submits to
    path('clock-in/', views.clock_in, name='clock_in'),

    # URL that the clock-out form submits to
    path('clock-out/', views.clock_out, name='clock_out'),
]
