from django.core.exceptions import ValidationError
from django.db import transaction

from apps.books.models import Book
from .models import Order, OrderItem


@transaction.atomic
def update_order_status(order_id, new_status):
    """Update status and keep inventory consistent when cancelling or reopening."""
    if new_status not in Order.Status.values:
        raise ValidationError("Choose a valid order status.")

    order = Order.objects.select_for_update().get(pk=order_id)
    old_status = order.status
    if old_status == new_status:
        return order

    items = list(OrderItem.objects.filter(order=order).order_by("book_id", "pk"))
    book_ids = sorted({item.book_id for item in items if item.book_id is not None})
    books = {
        book.pk: book
        for book in Book.objects.select_for_update().filter(pk__in=book_ids).order_by("pk")
    }

    if old_status == Order.Status.CANCELLED and new_status != Order.Status.CANCELLED:
        missing = [item.book_title for item in items if item.book_id is None or item.book_id not in books]
        insufficient = [
            f"{item.book_title} ({books[item.book_id].stock} available, {item.quantity} needed)"
            for item in items
            if item.book_id in books and books[item.book_id].stock < item.quantity
        ]
        if missing or insufficient:
            details = []
            if missing:
                details.append("deleted books: " + ", ".join(missing))
            if insufficient:
                details.append("insufficient stock: " + ", ".join(insufficient))
            raise ValidationError("This order cannot be reopened because " + "; ".join(details) + ".")
        for item in items:
            book = books[item.book_id]
            book.stock -= item.quantity
            book.save(update_fields=("stock", "updated_at"))

    if new_status == Order.Status.CANCELLED and old_status != Order.Status.CANCELLED:
        for item in items:
            book = books.get(item.book_id)
            if book is not None:
                book.stock += item.quantity
                book.save(update_fields=("stock", "updated_at"))

    order.status = new_status
    order.save(update_fields=("status", "updated_at"))
    return order
