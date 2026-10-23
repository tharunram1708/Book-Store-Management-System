from django import forms

from apps.orders.models import Order


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Order.Status.choices, label="Order status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.update({"class": "form-select form-select-sm"})
