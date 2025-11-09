from django.urls import path
from . import views

urlpatterns = [

    # path('', views.company_dashboard, name='company_dashboard'),
    path('', views.company_home, name='company_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.employees, name='employees'),
     path('employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('attendance/', views.attendance, name='attendance'),
    path('leaves/', views.leaves, name='leaves'),
    path('leaves/update/<int:id>/<str:status>/', views.update_leave_status, name='update_leave_status'),
    path('export-attendance-csv/', views.export_attendance_csv, name='export_attendance_csv'),
        path('holiday-calendar/', views.holiday_calendar, name='holiday_calendar'),

    path('subscription/', views.subscription, name='subscription'),
    path('logout/', views.logout, name='logout'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('update-attendance/', views.update_attendance, name='update_attendance'),

    #
    path('employee/<int:employee_id>/fire/', views.fire_employee, name='fire_employee'),
    path('holiday-calendar/', views.holiday_calendar, name='holiday_calendar'),
      path('holiday/<int:holiday_id>/edit/', views.edit_holiday, name='edit_holiday'),
    path('holiday/<int:holiday_id>/delete/', views.delete_holiday, name='delete_holiday'),



]