from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.http import require_http_methods

from . import utility
from .forms import OrderForm, QuoteForm
from .models import AuthorizedQuote, Order, Quote, Quote_Finishing
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
        quote.authorize_quote()
    return redirect(reverse(
        'ventas:quote_detail', kwargs={'pk': pk}))


class VentasView(TemplateView):
    template_name = 'ventas/index.html'


class OrdersView(ListView):
    template_name = 'ventas/orders.html'
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return all the Orders."""
        return Order.objects.all()


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'ventas/order_edit.html'

    def get(self, *args, **kwargs):
        """Determine whether or not page should be accessible."""
        pk = self.kwargs['pk']
        try:
            AuthorizedQuote.objects.get(quote_id=pk)
        except ObjectDoesNotExist:
            raise Http404("Quote does not exist.")
        return super(OrderCreateView, self).get(self.request)

    def form_valid(self, form):
        """Process a valid form."""
        pk = self.kwargs['pk']
        # retrieve auth quote
        error = False
        try:
            auth_quote = AuthorizedQuote.objects.get(quote_id=pk)
        except ObjectDoesNotExist:
            error = True
        if error is False:
            pack_inst = form['order_packaging_instructions'].value()
            delivery_addr = form['order_delivery_address'].value()
            notes = form['order_notes'].value()
            # call auth quote function to create order
            auth_quote.create_order(pack_inst, delivery_addr, notes)
            return redirect(reverse(
                'ventas:order_detail', kwargs={'pk': pk}))
        else:
            raise Http404("Quote does not exist.")


class OrderDetailView(DetailView):
    model = Order
    template_name = 'ventas/order_detail.html'


class QuotesView(ListView):
    template_name = 'ventas/quotes.html'
    context_object_name = 'latest_quote_list'

    def get_queryset(self):
        """Return all the Quotes."""
        return Quote.objects.all()


class QuoteCreateView(CreateView):
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


class QuoteDetailView(DetailView):
    model = Quote
    template_name = 'ventas/quote_detail.html'


class QuoteEditView(UpdateView):
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
