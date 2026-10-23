from django import forms
from apps.categories.models import Category
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "isbn", "price", "description", "category", "stock", "cover_image")
        widgets = {"description": forms.Textarea(attrs={"rows": 5}),
                   "price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
                   "stock": forms.NumberInput(attrs={"min": "0"})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if field.widget.__class__.__name__ == "Select" else "form-control"
    def clean_isbn(self):
        isbn = "".join(c for c in self.cleaned_data["isbn"] if c.isdigit() or c.upper() == "X").upper()
        if len(isbn) not in (10, 13):
            raise forms.ValidationError("Enter a valid 10 or 13 character ISBN.")
        query = Book.objects.filter(isbn=isbn)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise forms.ValidationError("A book with this ISBN already exists.")
        return isbn
    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price


class CatalogFilterForm(forms.Form):
    SORT_CHOICES = (
        ("title", "Title: A to Z"),
        ("-title", "Title: Z to A"),
        ("price", "Price: low to high"),
        ("-price", "Price: high to low"),
        ("-created_at", "Recently added"),
    )
    q = forms.CharField(required=False, label="Search", max_length=100)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="All categories")
    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, max_digits=10, label="Minimum price")
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, max_digits=10, label="Maximum price")
    sort = forms.ChoiceField(required=False, choices=SORT_CHOICES, initial="title")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
        self.fields["min_price"].widget.attrs.update({"placeholder": "From", "step": "0.01"})
        self.fields["max_price"].widget.attrs.update({"placeholder": "To", "step": "0.01"})

    def clean(self):
        cleaned = super().clean()
        low, high = cleaned.get("min_price"), cleaned.get("max_price")
        if low is not None and high is not None and low > high:
            self.add_error("max_price", "Maximum price must be at least the minimum price.")
        return cleaned
