from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("book_title", "book_isbn", "unit_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username", "shipping_name")
    readonly_fields = ("order_number", "user", "subtotal", "total", "created_at", "updated_at")
    inlines = (OrderItemInline,)

    def save_model(self, request, obj, form, change):
        if change:
            from .models import Order
            from .services import update_order_status
            with transaction.atomic():
                previous_status = Order.objects.only("status").get(pk=obj.pk).status
                if previous_status != obj.status:
                    try:
                        update_order_status(obj.pk, obj.status)
                    except ValidationError as error:
                        self.message_user(request, " ".join(error.messages), level=messages.ERROR)
                        obj.status = previous_status
                super().save_model(request, obj, form, change)
            return
        super().save_model(request, obj, form, change)


admin.site.register(OrderItem)
