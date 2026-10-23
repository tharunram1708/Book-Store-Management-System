from django import forms


class CheckoutForm(forms.Form):
    shipping_name = forms.CharField(max_length=150, label="Full name")
    shipping_phone = forms.CharField(max_length=20, label="Phone number")
    shipping_address = forms.CharField(label="Delivery address", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_shipping_phone(self):
        phone = self.cleaned_data["shipping_phone"].strip()
        digits = sum(character.isdigit() for character in phone)
        if digits < 7:
            raise forms.ValidationError("Enter a phone number with at least 7 digits.")
        return phone
