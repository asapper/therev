from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.http import require_http_methods

from .utility import OrderController, QuoteController
from .forms import OrderForm, QuoteForm
from .models import Order, Quote, Quote_Finishing
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
        QuoteController.authorize_quote(quote)
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
            Quote.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404("Quote does not exist.")
        return super(OrderCreateView, self).get(self.request)

    def form_valid(self, form):
        """Process a valid form."""
        pk = self.kwargs['pk']
        error = False
        try:
            quote = Quote.objects.get(pk=pk)
        except ObjectDoesNotExist:
            error = True
        if error is False:
            pack_inst = form['order_packaging_instructions'].value()
            delivery_addr = form['order_delivery_address'].value()
            notes = form['order_notes'].value()
            # call function to create order
            OrderController.create_order(
                quote, pack_inst, delivery_addr, notes)
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
        quote.set_executive(1)  # FIX THIS!
        # store imposing
        imposing, sheets = QuoteController.get_imposing(quote)
        quote.set_imposing(imposing)
        quote.set_total_sheets(sheets)
        # store materials
        quote.set_materials(form['materials'].value())
        # store finishings
        quote.set_finishings(form['finishings'].value())
        # store total price
        quote.set_total_price(QuoteController.get_total_price(quote))
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
        # store imposing if dimentions changed
        imposing, sheets = QuoteController.get_imposing(quote)
        quote.set_imposing(imposing)
        quote.set_total_sheets(sheets)
        # store materials
        quote.set_materials(form['materials'].value())
        # store finishings
        quote.set_finishings(form['finishings'].value())
        # store total price
        quote.set_total_price(QuoteController.get_total_price(quote))
        return redirect(reverse(
            'ventas:quote_detail', kwargs={'pk': quote.id}))
