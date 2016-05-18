from django.contrib import admin

from .models import Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'quote_name', 'quote_product_name',
                    'executive', 'quote_last_modified', 'quote_is_authorized',
                    'quote_is_approved', 'quote_total_price')
    list_filter = ['quote_last_modified', 'quote_is_authorized',
                   'quote_is_approved']
    search_fields = ['quote_name']


admin.site.register(Quote, QuoteAdmin)
