from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
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
            return redirect(reverse(
                'ventas:quote_detail', kwargs={'pk': quote.id}))
    else:
        form = QuoteForm()
    return render(request, 'ventas/quote_edit.html', {'form': form})


def edit_quote(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == "POST":
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.executive_id = 1
            quote.save()
            return redirect(reverse(
                'ventas:quote_detail', kwargs={'pk': quote.id}))
    else:
        form = QuoteForm(instance=quote)
    return render(request, 'ventas/quote_edit.html', {'form': form})


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
