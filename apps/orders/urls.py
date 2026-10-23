from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("", views.order_history, name="order_history"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
]
