# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/hr/', views.hr_signup, name='hr_signup'),
    path('signup/employee/', views.employee_signup, name='employee_signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('post_login_redirect/', views.post_login_redirect, name='post_login_redirect'),
]
