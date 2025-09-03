from django.urls import path
from . import views

app_name = "self_signup"

urlpatterns = [
    path("generate/", views.generate_employee_link, name="generate_link"),
    path("<uuid:token>/", views.employee_self_register, name="employee_self_register"),
]
