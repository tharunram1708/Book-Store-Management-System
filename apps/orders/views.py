from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from apps.books.models import Book
from apps.cart.models import Cart, CartItem
from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("cart_detail")
    profile = getattr(request.user, "profile", None)
    initial = {"shipping_name": request.user.get_full_name() or request.user.username}
    if profile:
        initial.update({"shipping_phone": profile.phone, "shipping_address": profile.address})
    form = CheckoutForm(request.POST or None, initial=initial if request.method == "GET" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                cart = Cart.objects.select_for_update().get(user=request.user)
                cart_items = list(cart.cart_items.select_related("book").order_by("book_id"))
                if not cart_items:
                    messages.info(request, "Your cart is empty.")
                    return redirect("cart_detail")
                book_ids = [item.book_id for item in cart_items]
                locked_books = Book.objects.select_for_update().filter(pk__in=book_ids).order_by("pk")
                books_by_id = {book.pk: book for book in locked_books}
                unavailable = []
                for item in cart_items:
                    book = books_by_id.get(item.book_id)
                    if book is None or item.quantity > book.stock:
                        available = book.stock if book else 0
                        unavailable.append(f"{item.book.title}: {available} available, {item.quantity} requested")
                if unavailable:
                    messages.error(request, "Stock changed before checkout. Please review your cart: " + "; ".join(unavailable))
                    return redirect("cart_detail")
                subtotal = sum((books_by_id[item.book_id].price * item.quantity for item in cart_items), Decimal("0.00"))
                order = Order.objects.create(
                    user=request.user,
                    shipping_name=form.cleaned_data["shipping_name"],
                    shipping_phone=form.cleaned_data["shipping_phone"],
                    shipping_address=form.cleaned_data["shipping_address"],
                    subtotal=subtotal,
                    total=subtotal,
                )
                order_items = []
                for item in cart_items:
                    book = books_by_id[item.book_id]
                    order_items.append(OrderItem(order=order, book=book, book_title=book.title,
                                                 book_isbn=book.isbn, unit_price=book.price, quantity=item.quantity))
                    book.stock -= item.quantity
                    book.save(update_fields=("stock", "updated_at"))
                OrderItem.objects.bulk_create(order_items)
                CartItem.objects.filter(cart=cart).delete()
        except Cart.DoesNotExist:
            messages.info(request, "Your cart is empty.")
            return redirect("cart_detail")
        messages.success(request, f"Order {order.order_number} was placed successfully.")
        return redirect("order_detail", pk=order.pk)
    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "items": cart.items})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related("items").all()
    return render(request, "orders/order_history.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
