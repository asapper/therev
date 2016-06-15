from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods

from .models import Order, Order_Process, Process
from .utility import OrderController
from .db_utility import DatabaseController
from .db_utility import (VALUE_OP_NUMBER, VALUE_CLIENT, VALUE_DESCRIPTION,
                         VALUE_MACHINE, VALUE_QUANTITY, VALUE_SHEETS,
                         VALUE_PROCESSES)


class ActiveOrdersView(ListView):
    template_name = 'control_produccion/active_orders.html'
    context_object_name = 'latest_active_orders_list'

    def get_queryset(self):
        """Return all active Orders."""
        return Order.objects.filter(order_is_finished=False)


class OrdersView(ListView):
    template_name = 'control_produccion/orders.html'
    context_object_name = 'latest_order_list'

    def get(self, request, *args, **kwargs):
        # query Sunhive db
        op_list, results = DatabaseController.get_orders()
        # create objects based on result from query
        for item in results:
            duplicate = False
            try:
                order = Order.objects.create(
                    order_op_number=item[VALUE_OP_NUMBER],
                    order_client=item[VALUE_CLIENT],
                    order_description=item[VALUE_DESCRIPTION],
                    order_machine=item[VALUE_MACHINE],
                    order_quantity=item[VALUE_QUANTITY],
                    order_total_sheets=item[VALUE_SHEETS])
            except IntegrityError:
                duplicate = True
            if duplicate is False:
                # create Order_Process objects for each process
                for process_name in item[VALUE_PROCESSES]:
                    try:
                        # retrieve Process instance
                        process_instance = Process.objects.get(
                            process_name=process_name)
                    except ObjectDoesNotExist:
                        continue
                    # create Order Process object if Process found
                    Order_Process.objects.create(
                        order=order,
                        process=process_instance)
        # retrieve all Orders not in result from query
        finished_orders = Order.objects.exclude(order_op_number__in=op_list)
        # finish those Orders
        for order in finished_orders:
            order.set_finished()
        return super(OrdersView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """Return all the Orders."""
        return Order.objects.all().order_by('order_op_number')

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
