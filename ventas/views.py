from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views import generic

from .forms import QuoteForm
from .models import Quote


def new_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.executive_id = 1
            quote.save()
            print("Quote saved!")
            return redirect(reverse(
                'ventas:quote_detail', kwargs={'pk': quote.id}))
        else:
            print("Quote invalid!")
    else:
        form = QuoteForm()
    return render(request, 'ventas/new_quote.html', {'form': form})


class VentasView(generic.base.TemplateView):
    template_name = 'ventas/index.html'


class QuotesView(generic.ListView):
    template_name = 'ventas/quotes.html'
    context_object_name = 'latest_quote_list'

    def get_queryset(self):
        """Return all the Quotes."""
        return Quote.objects.all()


class QuoteDetailView(generic.DetailView):
    model = Quote
    template_name = 'ventas/quote_detail.html'
