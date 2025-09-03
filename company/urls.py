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

    path('subscription/', views.subscription, name='subscription'),
    path('logout/', views.logout, name='logout'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),

    #
    path('employee/<int:employee_id>/fire/', views.fire_employee, name='fire_employee'),


]