from django import forms
from .models import Trade

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        exclude = ['user']  # We'll set the user manually in the view
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
            'exit_date': forms.DateInput(attrs={'type': 'date'}),
        }

    # Optional: Custom validation or formatting can go here later
