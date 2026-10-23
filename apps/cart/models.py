from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopping_cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def items(self):
        return self.cart_items.select_related("book", "book__category")

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items), start=0)

    @property
    def total(self):
        # Day 2 has no shipping or tax charges, so total equals subtotal.
        return self.subtotal

    @property
    def item_count(self):
        return sum(item.quantity for item in self.cart_items.all())

    def __str__(self):
        return f"Cart for {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("cart", "book"), name="unique_book_per_cart")]
        ordering = ["created_at"]

    @property
    def line_total(self):
        return self.quantity * self.book.price

    def __str__(self):
        return f"{self.quantity} × {self.book.title}"
