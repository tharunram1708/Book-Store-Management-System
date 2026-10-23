from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm
from .models import Category


def category_list(request):
    return render(request, "categories/category_list.html", {"categories": Category.objects.annotate(book_count=Count("books"))})


@staff_member_required(login_url="login")
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f'Category “{category.name}” was created.')
        return redirect("category_list")
    return render(request, "categories/category_form.html", {"form": form, "heading": "Add a category"})


@staff_member_required(login_url="login")
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category details were updated.")
        return redirect("category_list")
    return render(request, "categories/category_form.html", {"form": form, "heading": "Update category", "category": category})


@staff_member_required(login_url="login")
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        try:
            category.delete()
            messages.success(request, "Category was deleted.")
        except ProtectedError:
            messages.error(request, "This category still contains books. Move or delete those books first.")
        return redirect("category_list")
    return render(request, "categories/category_confirm_delete.html", {"category": category})
