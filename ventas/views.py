from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.http import require_http_methods

from .utility import OrderController, QuoteController
from .forms import OrderForm, QuoteForm
from .models import Order, Quote, Quote_Finishing
from recursos.models import Finishing, Material


@require_http_methods(["POST"])
def authorize_quote(request, pk):
    """Authorizes quote if POST received and redirects to quote detail page."""
    response = None
    error = False
    try:
        quote = Quote.objects.get(pk=pk)
    except ObjectDoesNotExist:
        error = True
        response = HttpResponseNotFound("Order not found")
    if error is False:
        QuoteController.authorize_quote(quote)
        response = redirect(reverse(
            'ventas:quote_detail', kwargs={'pk': pk}))
    return response


class VentasView(TemplateView):
    template_name = 'ventas/index.html'


class OrdersView(ListView):
    template_name = 'ventas/orders.html'
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return all the Orders."""
        return Order.objects.all()

    @require_http_methods(["POST"])
    def start_order(self, pk):
        """
        Retrieve order with given pk and call
        helper function to start this Order.
        """
        try:
            order = Order.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Order not found")
        OrderController.start_order(order)
        return redirect(reverse(
            'ventas:order_detail', kwargs={'pk': pk}))

    @require_http_methods(["POST"])
    def start_finishing(self, pk, finishing_id):
        """
        Retrieve order with given pk, as well as QuoteFinishing with
        quote id and given finishing id, and call helper function
        to start that Finishing.
        """
        try:
            order = Order.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Order not found")
        if order.order_is_started is True:
            try:
                quote_finishing_instance = Quote_Finishing.objects.get(
                    quote_id=order.get_quote_id(),
                    finishing_id=finishing_id)
            except ObjectDoesNotExist:
                return HttpResponseNotFound("Finishing not found")
            OrderController.start_finishing(quote_finishing_instance)
            return redirect(reverse(
                'ventas:order_detail', kwargs={'pk': pk}))
        return HttpResponseNotFound("Order not started")


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
            return HttpResponseNotFound("Quote does not exist.")
        return super(OrderCreateView, self).get(self.request)

    def form_valid(self, form):
        """Process a valid form."""
        pk = self.kwargs['pk']
        try:
            quote = Quote.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Quote not found")
        pack_inst = form['order_packaging_instructions'].value()
        delivery_addr = form['order_delivery_address'].value()
        notes = form['order_notes'].value()
        # call function to create order
        order = OrderController.create_order(
            quote, pack_inst, delivery_addr, notes)
        return redirect(reverse(
            'ventas:order_detail', kwargs={'pk': order.id}))


class OrderDetailView(DetailView):
    model = Order
    template_name = 'ventas/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order = kwargs['object']
        # add in QuoteFinishing information
        context['quote_finishing_list'] = Quote_Finishing.objects.filter(
            quote_id=order.get_quote_id())
        return context


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
        materials = []
        for id in form['materials'].value():
            try:
                material = Material.objects.get(pk=id)
            except ObjectDoesNotExist:
                continue
            materials.append(material)
        quote.set_materials(materials)
        # store finishings
        finishings = []
        for id in form['finishings'].value():
            try:
                finishing = Finishing.objects.get(pk=id)
            except ObjectDoesNotExist:
                continue
            finishings.append(finishing)
        quote.set_finishings(finishings)
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
        quote = form.save(commit=False)
        # store imposing if dimentions changed
        imposing, sheets = QuoteController.get_imposing(quote)
        quote.set_imposing(imposing)
        quote.set_total_sheets(sheets)
        # store materials
        materials = []
        for id in form['materials'].value():
            try:
                material = Material.objects.get(pk=id)
            except ObjectDoesNotExist:
                continue
            materials.append(material)
        quote.set_materials(materials)
        # store finishings
        finishings = []
        for id in form['finishings'].value():
            try:
                finishing = Finishing.objects.get(pk=id)
            except ObjectDoesNotExist:
                continue
            finishings.append(finishing)
        quote.set_finishings(finishings)
        # store total price
        quote.set_total_price(QuoteController.get_total_price(quote))
        return redirect(reverse(
            'ventas:quote_detail', kwargs={'pk': quote.id}))
