from django.http import HttpResponse
from django.views import generic

from .models import Quote


def index(request):
    return HttpResponse("Hello, world. You're at the Ventas index.")


class QuotesView(generic.ListView):
    template_name = 'ventas/quotes.html'
    context_object_name = 'latest_quote_list'

    def get_queryset(self):
        """Return all the Quotes."""
        return Quote.objects.all()


class QuoteDetailView(generic.DetailView):
    model = Quote
    template_name = 'ventas/quote_detail.html'
