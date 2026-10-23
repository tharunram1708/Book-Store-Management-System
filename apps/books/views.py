from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BookForm, CatalogFilterForm
from .models import Book

def book_list(request):
    form = CatalogFilterForm(request.GET or None)
    books = Book.objects.select_related("category").all()
    if form.is_valid():
        filters = form.cleaned_data
        query = filters.get("q", "").strip()
        if query:
            books = books.filter(title__icontains=query) | books.filter(author__icontains=query) | books.filter(isbn__icontains=query)
        if filters.get("category"):
            books = books.filter(category=filters["category"])
        if filters.get("min_price") is not None:
            books = books.filter(price__gte=filters["min_price"])
        if filters.get("max_price") is not None:
            books = books.filter(price__lte=filters["max_price"])
        books = books.order_by(filters.get("sort") or "title")
    return render(request, "books/book_list.html", {"books": books, "filter_form": form})

def book_detail(request, pk):
    book = get_object_or_404(Book.objects.select_related("category"), pk=pk)
    return render(request, "books/book_detail.html", {"book": book})

@staff_member_required(login_url="login")
def book_create(request):
    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        book = form.save()
        messages.success(request, f'“{book.title}” was added.')
        return redirect("book_detail", pk=book.pk)
    return render(request, "books/book_form.html", {"form": form, "heading": "Add a book"})

@staff_member_required(login_url="login")
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book details were updated.")
        return redirect("book_detail", pk=book.pk)
    return render(request, "books/book_form.html", {"form": form, "heading": "Update book", "book": book})

@staff_member_required(login_url="login")
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        title = book.title
        book.delete()
        messages.success(request, f'“{title}” was deleted.')
        return redirect("book_list")
    return render(request, "books/book_confirm_delete.html", {"book": book})
