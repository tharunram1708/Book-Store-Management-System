from django.core.validators import MinValueValidator
from django.db import models
from apps.categories.models import Category

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    stock = models.PositiveIntegerField(default=0)
    cover_image = models.ImageField(upload_to="book_covers/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["title"]
    def __str__(self):
        return self.title
