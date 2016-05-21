from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic

from .forms import QuoteForm
from .models import Quote
from .models import Quote_Finishing
from recursos.models import Finishing


def new_quote(request):
    """Creates a new quote based on the form returned."""
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            # assign executive that made this quote
            quote.executive_id = 1  # FIX THIS!
            quote.save()  # save quote
            # store materials
            quote.materials.set(form['materials'].value())
            # store finishings
            quote.finishings.clear()
            for finishing_id in form['finishings'].value():
                finishing = Finishing.objects.get(pk=finishing_id)
                Quote_Finishing.objects.create(
                    quote=quote,
                    finishing=finishing)
            return redirect(reverse(
                'ventas:quote_detail', kwargs={'pk': quote.id}))
    else:
        form = QuoteForm()
    return render(request, 'ventas/quote_edit.html', {'form': form})


def edit_quote(request, pk):
    """Edits and updates a Quote based on the form returned."""
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == "POST":
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            quote = form.save(commit=False)
            # assign executive that made this quote
            quote.executive_id = 1  # FIX THIS!
            # clear old, keep only new list of materials
            quote.materials.set(form['materials'].value())
            # store finishings
            quote.finishings.clear()
            for finishing_id in form['finishings'].value():
                finishing = Finishing.objects.get(pk=finishing_id)
                Quote_Finishing.objects.create(
                    quote=quote,
                    finishing=finishing)
            # save quote
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
