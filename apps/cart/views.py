from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from apps.books.models import Book
from .forms import QuantityForm
from .models import Cart, CartItem


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart/cart_detail.html", {"cart": cart, "items": cart.items})


@login_required
def cart_add(request, book_id):
    if request.method != "POST":
        return redirect("book_detail", pk=book_id)
    book = get_object_or_404(Book, pk=book_id)
    form = QuantityForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Enter a quantity from 1 to 999.")
        return redirect("book_detail", pk=book.pk)
    requested = form.cleaned_data["quantity"]
    with transaction.atomic():
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.select_for_update().get(pk=cart.pk)
        book = Book.objects.select_for_update().get(pk=book.pk)
        item = CartItem.objects.select_for_update().filter(cart=cart, book=book).first()
        new_quantity = requested + (item.quantity if item else 0)
        if book.stock < new_quantity:
            messages.error(request, f"Only {book.stock} copies of “{book.title}” are in stock.")
            return redirect("book_detail", pk=book.pk)
        if item:
            item.quantity = new_quantity
            item.save(update_fields=("quantity", "updated_at"))
        else:
            CartItem.objects.create(cart=cart, book=book, quantity=requested)
    messages.success(request, f'Added {requested} × “{book.title}” to your cart.')
    return redirect("cart_detail")


@login_required
def cart_update(request, item_id):
    if request.method != "POST":
        return redirect("cart_detail")
    form = QuantityForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Enter a quantity from 1 to 999.")
        return redirect("cart_detail")
    requested = form.cleaned_data["quantity"]
    with transaction.atomic():
        cart = Cart.objects.select_for_update().get(user=request.user)
        item = get_object_or_404(CartItem.objects.select_related("book"), pk=item_id, cart=cart)
        book = Book.objects.select_for_update().get(pk=item.book_id)
        if requested > book.stock:
            messages.error(request, f"Only {book.stock} copies of “{book.title}” are in stock.")
        else:
            CartItem.objects.filter(pk=item.pk, cart__user=request.user).update(quantity=requested)
            messages.success(request, "Cart quantity updated.")
    return redirect("cart_detail")


@login_required
def cart_remove(request, item_id):
    if request.method == "POST":
        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(user=request.user)
            item = get_object_or_404(CartItem, pk=item_id, cart=cart)
            item.delete()
        messages.success(request, "Item removed from your cart.")
    return redirect("cart_detail")
