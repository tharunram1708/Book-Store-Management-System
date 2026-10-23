from django import forms


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=999, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quantity"].widget.attrs.update({"class": "form-control", "min": 1, "max": 999})
