from django.urls import path
from . import views

app_name = "subcription"

urlpatterns = [
    path("subscription/", views.Subscription, name="subscription"),
    path("order/<int:plan_id>/", views.create_order, name="create_order"),
]
