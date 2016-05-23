from django import forms

from .models import Quote


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        exclude = ['quote_date_created', 'quote_last_modified',
                   'quote_is_authorized', 'quote_is_approved',
                   'quote_total_price', 'quote_imposing_per_sheet',
                   'quote_total_sheets', 'executive',]
