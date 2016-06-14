from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods

from .models import Order, Order_Process
from .utility import OrderController


class OrdersView(ListView):
    template_name = 'control_produccion/orders.html'
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return all the Orders."""
        return Order.objects.all()

    @require_http_methods(["POST"])
    def start_process(self, pk, process_id):
        """
        Retrieve order with given pk, as well as OrderProcess with
        order id and given process id, and call helper function
        to start that Process.
        """
        order = get_object_or_404(Order, pk=pk)  # get order
        # get order process
        order_process_instance = get_object_or_404(
            Order_Process,
            order_id=order.id,
            process_id=process_id)
        msg = OrderController.start_process(order_process_instance)
        messages.info(self, msg)  # send returned messages
        return redirect(reverse(
            'control_produccion:order_detail', kwargs={'pk': pk}))

    @require_http_methods(["POST"])
    def finish_process(self, pk, process_id):
        """
        Retrieve order with given pk, as well as OrderProcess with
        order id and given process id, and call helper function
        to finish that Process.
        """
        order = get_object_or_404(Order, pk=pk)  # get order
        # get order process
        order_process_instance = get_object_or_404(
            Order_Process,
            order_id=order.id,
            process_id=process_id)
        msg = OrderController.finish_process(order_process_instance)
        messages.info(self, msg)  # send returned messages
        return redirect(reverse(
            'control_produccion:order_detail', kwargs={'pk': pk}))


class OrderDetailView(DetailView):
    model = Order
    template_name = 'control_produccion/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order = kwargs['object']
        # add in Processes information
        processes = Order_Process.objects.filter(
            order_id=order.id)
        context['order_process_list'] = processes
        return context


class ProduccionView(TemplateView):
    template_name = 'control_produccion/index.html'
