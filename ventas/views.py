from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.shortcuts import redirect
from django.views import generic
from django.views.decorators.http import require_http_methods

from . import utility
from .forms import QuoteForm
from .models import AuthorizedQuote
from .models import Quote
from .models import Quote_Finishing
from recursos.models import Finishing


@require_http_methods(["POST"])
def authorize_quote(request, pk):
    """Authorizes quote if POST received and redirects to quote detail page."""
    error = False
    try:
        quote = Quote.objects.get(pk=pk)
    except ObjectDoesNotExist:
        error = True
    if error is False:
        if quote.quote_is_authorized is False:
            try:  # authorize quote
                AuthorizedQuote.objects.create(quote=quote)
            except IntegrityError:
                error = True
            if error is False:
                quote.quote_is_authorized = True  # update quote
                quote.save()
    return redirect(reverse(
        'ventas:quote_detail', kwargs={'pk': pk}))


class QuoteCreateView(generic.edit.CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'ventas/quote_edit.html'

    def form_valid(self, form):
        """Process a valid form."""
        quote = form.save(commit=False)
        # assign executive that made this quote
        quote.executive_id = 1  # FIX THIS!
        # store imposing
        imposing, sheets = utility.get_imposing(quote)
        quote.quote_imposing_per_sheet = imposing
        quote.quote_total_sheets = sheets
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
        # store total price
        quote.quote_total_price = utility.get_total_price(quote)
        quote.save()  # save quote
        return redirect(reverse(
            'ventas:quote_detail', kwargs={'pk': quote.id}))


class QuoteEditView(generic.edit.UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'ventas/quote_edit.html'

    def form_valid(self, form):
        """Save an edited Quote."""
        quote = form.save(commit=False)
        # store imposing if dimentions changed
        imposing, sheets = utility.get_imposing(quote)
        quote.quote_imposing_per_sheet = imposing
        quote.quote_total_sheets = sheets
        # clear old, keep only new list of materials
        quote.materials.set(form['materials'].value())
        # store finishings
        quote.finishings.clear()
        for finishing_id in form['finishings'].value():
            finishing = Finishing.objects.get(pk=finishing_id)
            Quote_Finishing.objects.create(
                quote=quote,
                finishing=finishing)
        # store total price
        quote.quote_total_price = utility.get_total_price(quote)
        quote.save()  # save quote
        return redirect(reverse(
            'ventas:quote_detail', kwargs={'pk': quote.id}))


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
