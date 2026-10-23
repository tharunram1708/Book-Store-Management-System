from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("book_title", "book_isbn", "unit_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("order_number", "user__username", "shipping_name")
    readonly_fields = ("order_number", "user", "subtotal", "total", "created_at", "updated_at")
    inlines = (OrderItemInline,)


admin.site.register(OrderItem)
