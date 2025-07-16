from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from django.core.exceptions import ValidationError
from .models import Trade
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            "instrument",
            "position_size",
            "entry_price",
            "exit_price",
            "entry_date",
            "exit_date",
            "outcome",
            "notes",
        ]
        widgets = {
            # give our instrument field an ID for the autocomplete hook:
            "instrument": forms.TextInput(
                attrs={
                    "id": "instrument-field",
                    "autocomplete": "off",
                    "class": "form-control",
                }
            ),
            # bootstrap‐style on the rest:
            "entry_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "exit_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "position_size": forms.NumberInput(attrs={"class": "form-control"}),
            "entry_price": forms.NumberInput(attrs={"class": "form-control"}),
            "exit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "outcome": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize Crispy helper
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field(
                "instrument",
                css_class="form-control",
                aria_required="true",
                placeholder="e.g. AAPL",
            ),
            Field(
                "position_size",
                css_class="form-control",
                type="number",
                step="0.01",
                aria_required="true",
            ),
            Field(
                "entry_price",
                css_class="form-control",
                type="number",
                step="0.01",
                aria_required="true",
            ),
            Field("exit_price", css_class="form-control", type="number", step="0.01"),
            Field(
                "entry_date",
                css_class="form-control",
                type="date",
                aria_required="true",
            ),
            Field("exit_date", css_class="form-control", type="date"),
            Field("outcome", css_class="form-select", aria_required="true"),
            Field("notes", css_class="form-control", rows="3"),
            Submit("submit", "Save Trade", css_class="btn btn-primary mt-2"),
        )

    def clean_position_size(self):
        size = self.cleaned_data.get("position_size")
        if size is not None and size <= 0:
            raise ValidationError("Position size must be greater than zero.")
        return size

    def clean_entry_price(self):
        price = self.cleaned_data.get("entry_price")
        if price is not None and price <= 0:
            raise ValidationError("Entry price must be greater than zero.")
        return price

    def clean_exit_price(self):
        price = self.cleaned_data.get("exit_price")
        # exit_price is optional, only validate if provided
        if price is not None and price < 0:
            raise ValidationError("Exit price cannot be negative.")
        return price

    def clean(self):
        cleaned = super().clean()
        entry = cleaned.get("entry_date")
        exit_ = cleaned.get("exit_date")

        # If exit_date provided, it must not be before entry_date
        if entry and exit_:
            if exit_ < entry:
                raise ValidationError(
                    {"exit_date": "Exit date cannot be earlier than entry date."}
                )

        return cleaned


class CSVImportForm(forms.Form):
    file = forms.FileField(
        label="Select CSV file",
        help_text="Columns: instrument,position_size,entry_price,exit_price,entry_date,exit_date,outcome,notes",
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
