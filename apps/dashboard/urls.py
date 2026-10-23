from django.urls import path
from .views import admin_dashboard, admin_order_status, home
urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/orders/<int:pk>/status/", admin_order_status, name="admin_order_status"),
]
