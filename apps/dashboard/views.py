from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.books.models import Book
from apps.categories.models import Category
from apps.orders.models import Order
from apps.orders.services import update_order_status
from .forms import OrderStatusForm

def home(request):
    return redirect("book_list")


@staff_member_required(login_url="login")
def admin_dashboard(request):
    completed_statuses = (Order.Status.CONFIRMED, Order.Status.SHIPPED, Order.Status.DELIVERED)
    context = {
        "book_count": Book.objects.count(),
        "order_count": Order.objects.count(),
        "sales_total": Order.objects.filter(status__in=completed_statuses).aggregate(total=Sum("total"))["total"] or Decimal("0.00"),
        "low_stock_count": Book.objects.filter(stock__lte=5).count(),
        "low_stock_books": Book.objects.select_related("category").filter(stock__lte=5).order_by("stock", "title")[:8],
        "recent_orders": Order.objects.select_related("user").prefetch_related("items")[:10],
        "category_count": Category.objects.count(),
        "low_stock_threshold": 5,
        "status_form": OrderStatusForm(),
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@staff_member_required(login_url="login")
def admin_order_status(request, pk):
    if request.method != "POST":
        return redirect("admin_dashboard")
    order = get_object_or_404(Order, pk=pk)
    form = OrderStatusForm(request.POST)
    if form.is_valid():
        try:
            update_order_status(order.pk, form.cleaned_data["status"])
        except ValidationError as error:
            messages.error(request, " ".join(error.messages))
        else:
            messages.success(request, f"Order {order.order_number} was updated.")
    else:
        messages.error(request, "Choose a valid order status.")
    return redirect("admin_dashboard")
