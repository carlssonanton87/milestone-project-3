from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from django.core.exceptions import ValidationError
from .models import Trade
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# ---------------- Trade Entry/Edit Form -----------------


class TradeForm(forms.ModelForm):
    """
    Main form for creating and editing a trade.
    Uses Crispy Forms for Bootstrap styling and includes custom validation.
    """

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
            # Autocomplete hook for 'instrument' field
            "instrument": forms.TextInput(
                attrs={
                    "id": "instrument-field",
                    "autocomplete": "off",
                    "class": "form-control",
                }
            ),
            # Bootstrap styles for all fields
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
        """
        Set up crispy-forms helper for consistent styling and accessible layout.
        """
        super().__init__(*args, **kwargs)

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

    # ----------- Field-level Validation -----------

    def clean_position_size(self):
        """
        Ensure position size is positive (required for correct trade tracking).
        """
        size = self.cleaned_data.get("position_size")
        if size is not None and size <= 0:
            raise ValidationError("Position size must be greater than zero.")
        return size

    def clean_entry_price(self):
        """
        Entry price must also be positive.
        """
        price = self.cleaned_data.get("entry_price")
        if price is not None and price <= 0:
            raise ValidationError("Entry price must be greater than zero.")
        return price

    def clean_exit_price(self):
        """
        If user entered an exit price, ensure it is not negative.
        """
        price = self.cleaned_data.get("exit_price")
        if price is not None and price < 0:
            raise ValidationError("Exit price cannot be negative.")
        return price

    # ----------- Form-level Validation -----------

    def clean(self):
        """
        Additional validation:
        - If both entry and exit date provided, exit cannot be before entry.
        """
        cleaned = super().clean()
        entry = cleaned.get("entry_date")
        exit_ = cleaned.get("exit_date")

        if entry and exit_:
            if exit_ < entry:
                raise ValidationError(
                    {"exit_date": "Exit date cannot be earlier than entry date."}
                )

        return cleaned


# ---------------- CSV Import Form -----------------


class CSVImportForm(forms.Form):
    """
    Simple form for uploading a CSV file for bulk import of trades.
    """

    file = forms.FileField(
        label="Select CSV file",
        help_text="Columns: instrument,position_size,entry_price,exit_price,entry_date,exit_date,outcome,notes",
    )


# -------------- Custom Signup Form -----------------


class CustomUserCreationForm(UserCreationForm):
    """
    Extends Django's built-in user creation form to require an email field.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
