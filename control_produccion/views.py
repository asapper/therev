# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import DatabaseError, IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.template.response import SimpleTemplateResponse
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods

from .models import Order, Order_Process, Process
from .utility import OrderController
from .db_utility import DatabaseController
from .db_utility import (VALUE_OP_NUMBER, VALUE_CLIENT, VALUE_DESCRIPTION,
                         VALUE_MACHINE, VALUE_QUANTITY, VALUE_SHEETS,
                         VALUE_PROCESSES, VALUE_DUE_DATE, VALUE_DATE_CREATED)


class ActiveOrdersRefreshView(ListView):
    template_name = 'control_produccion/active_orders_table.html'
    context_object_name = 'latest_active_orders_list'

    def get_context_data(self, **kwargs):
        """Add process list to context and return context data."""
        context = super(ActiveOrdersRefreshView, self).get_context_data(
            **kwargs)
        processes = Process.objects.all()
        context['process_list'] = processes
        return context

    def get_queryset(self):
        """Return all active Orders."""
        return Order.objects.filter(
            order_is_finished=False).order_by('order_due_date')


class ActiveOrdersView(TemplateView):
    template_name = 'control_produccion/active_orders.html'

    def refresh_database(self):
        """Connect to Sunhive db and update records on Active Orders."""
        # query Sunhive db
        try:
            op_list, results = DatabaseController.get_orders()
        except DatabaseError:  # if not able to connect to Sunhive db
            return HttpResponse()
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
                    order_total_sheets=item[VALUE_SHEETS],
                    order_due_date=item[VALUE_DUE_DATE],
                    order_date_created=item[VALUE_DATE_CREATED])
            except IntegrityError:
                duplicate = True
                # get duplicate order
                old_order = Order.objects.get(
                    order_op_number=item[VALUE_OP_NUMBER])
                # verify due date
                if old_order.order_due_date != item[VALUE_DUE_DATE]:
                    # if different, update due date
                    old_order.set_due_date(item[VALUE_DUE_DATE])
                # else, no change ought to be made
            if duplicate is False:
                # create Order_Process objects for each process
                for process_name in item[VALUE_PROCESSES]:
                    try:
                        # retrieve Process instance
                        process_instance = Process.objects.get(
                            process_name=process_name)
                    except ObjectDoesNotExist:
                        Process.objects.create(process_name=process_name)
                        messages.info(
                            self,
                            ("Orden #{}: nuevo proceso {} agregado a la "
                             "base de datos").format(
                                order.id,
                                process_name))
                        continue
                    # create Order Process object if Process found
                    Order_Process.objects.create(
                        order=order,
                        process=process_instance)
        # retrieve all Orders not in result from query
        finished_orders = Order.objects.exclude(order_op_number__in=op_list)
        # finish those Orders
        for order in finished_orders:
            if order.get_is_finished() is False:
                order.set_finished()
        return HttpResponse()


class OrdersView(ListView):
    template_name = 'control_produccion/orders.html'
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return all the Orders."""
        return Order.objects.all().order_by('-order_op_number')

    def get_context_data(self, **kwargs):
        """
        Add number of recent (< 30 days back) orders
        to context and return context data.
        """
        context = super(OrdersView, self).get_context_data(
            **kwargs)
        last_month = timezone.now() - datetime.timedelta(days=31)
        recent_orders = Order.objects.filter(
            order_due_date__gt=last_month).count()
        context['recent_orders'] = recent_orders
        return context

    @require_http_methods(["POST"])
    def pause_all_processes(self):
        """
        Retrieve all active Order_Process'es and call helper
        function to pause each of them.
        """
        username = self.POST.get('username')
        password = self.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:  # if user is authenticated
            level, msg = OrderController.pause_all_processes(user)
            messages.add_message(self, level, msg)  # send returned messages
        else:  # user authentication failed
            messages.warning(
                self, "Procesos no pausados! Usuario/contraseña incorrecta.")
        return redirect(reverse('control_produccion:orders'))


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

    @require_http_methods(["POST"])
    def start_process(self, pk, process_id):
        """
        Retrieve order_process with given pk, as well as OrderProcess with
        order id and given process id, and call helper function
        to start that Process.
        """
        # get order process
        order_process_instance = get_object_or_404(
            Order_Process,
            order_id=pk,
            process_id=process_id)
        level, msg = OrderController.start_process(order_process_instance)
        messages.add_message(self, level, msg)  # send returned messages
        return redirect(reverse(
            'control_produccion:order_detail', kwargs={'pk': pk}))

    @require_http_methods(["POST"])
    def finish_process(self, pk, process_id):
        """
        Retrieve order_process with given order pk and process id,
        or raise a 404, and call helper function
        to finish that Process.
        """
        # get order process
        order_process_instance = get_object_or_404(
            Order_Process,
            order_id=pk,
            process_id=process_id)
        level, msg = OrderController.finish_process(order_process_instance)
        messages.add_message(self, level, msg)  # send returned messages
        return redirect(reverse(
            'control_produccion:order_detail', kwargs={'pk': pk}))

    @require_http_methods(["POST"])
    def pause_process(self, pk, process_id):
        """
        Retrieve order_process with given order pk and process id,
        or raise a 404, and call helper function
        to pause that Process.
        """
        # get order process
        order_process_instance = get_object_or_404(
            Order_Process,
            order_id=pk,
            process_id=process_id)
        level, msg = OrderController.pause_process(order_process_instance)
        messages.add_message(self, level, msg)  # send returned messages
        return redirect(reverse(
            'control_produccion:order_detail', kwargs={'pk': pk}))

    @require_http_methods(["POST"])
    def resume_process(self, pk, process_id):
        """
        Retrieve order_process with given order pk and process id,
        or raise a 404, and call helper function
        to resume that Process.
        """
        # get order process
        order_process_instance = get_object_or_404(
            Order_Process,
            order_id=pk,
            process_id=process_id)
        level, msg = OrderController.resume_process(order_process_instance)
        messages.add_message(self, level, msg)  # send returned messages
        return redirect(reverse(
            'control_produccion:order_detail', kwargs={'pk': pk}))


class ProduccionView(TemplateView):
    template_name = 'control_produccion/index.html'


class TimeProcessesView(TemplateView):
    template_name = 'control_produccion/time_processes.html'


class TimeProcessesResultView(TemplateView):
    template_name = 'control_produccion/time_processes_result.html'

    @require_http_methods(["POST"])
    def process_remove_time(self):
        """
        Receives the data input in the Time Process view,
        retrieves the associated Order Process instance, and
        calls helper function to remove the start time of the
        retrieved Order Process instance.
        """
        # call helper function to process input
        order_process, messages = (
            OrderController.process_input_time_view(self))
        # call helper function to remove time
        msg = OrderController.remove_start_time(order_process)
        messages.append(msg)
        # load context
        context = {'order_process': order_process}
        # add messages
        context['messages'] = messages
        return SimpleTemplateResponse(
            template='control_produccion/time_processes_result.html',
            context=context)

    @require_http_methods(["POST"])
    def process_input(self):
        """
        Receives the data input in the Time Process view,
        retrieves the associated Order Process instance, and
        calls helper function to either start or finish the
        retrieved Order Process instance.
        """
        # call helper function to process input
        order_process, messages = (
            OrderController.process_input_time_view(self))
        # load context
        context = {'order_process': order_process}
        # add messages
        context['messages'] = messages
        return SimpleTemplateResponse(
            template='control_produccion/time_processes_result.html',
            context=context)


class AnalyticsView(TemplateView):
    template_name = 'control_produccion/analytics.html'

    def get_process_times(self):
        """
        Call utility function to get the duration times
        for all the processes.
        """
        return OrderController.get_avg_process_finish_time()

    def get_general_top_most_present_processes(self):
        """
        Call utility function to get the top 5 process
        most often seen in all the Orders.
        """
        return OrderController.get_general_top_five_most_often_present_processes()

    def get_last_week_top_most_present_processes(self):
        """
        Call utility function to get the top 5 process
        most often seen in Orders created last week.
        """
        return OrderController.get_last_week_top_five_most_often_present_processes()

    def get_last_month_top_most_present_processes(self):
        """
        Call utility function to get the top 5 process
        most often seen in Orders created last month.
        """
        return OrderController.get_last_month_top_five_most_often_present_processes()

    def get_general_top_most_frequent_clients(self):
        """
        Call utility function to get the top 5 most
        frequent clients in all orders.
        """
        return OrderController.get_general_top_five_most_frequent_clients()

    def get_last_week_top_most_frequent_clients(self):
        """
        Call utility function to get the top 5 most
        frequent clients in Orders created last week.
        """
        return OrderController.get_last_week_top_five_most_frequent_clients()

    def get_last_month_top_most_frequent_clients(self):
        """
        Call utility function to get the top 5 most
        frequent clients in Orders created last month.
        """
        return OrderController.get_last_month_top_five_most_frequent_clients()

    def get_process_pause_times(self):
        """
        Call utility funcion to get the average pause times
        for each of the Processes.
        """
        return OrderController.get_avg_process_pause_time()

    def get_workers_times(self):
        """
        Call utility function to get the number of processes finished
        per user.
        """
        return OrderController.get_workers_processes_finished_and_times()

    def get_general_sheets_printed(self):
        """
        Call utility function to get the total sheets
        printed per machine.
        """
        return OrderController.get_general_printed_sheets_per_machine()

    def get_last_month_sheets_printed(self):
        """
        Call utility function to get the total sheets
        printed last month (30 days back) per machine.
        """
        return OrderController.get_last_month_printed_sheets_per_machine()

    def get_last_week_sheets_printed(self):
        """
        Call utility function to get the total sheets
        printed last week (7 days back) per machine.
        """
        return OrderController.get_last_week_printed_sheets_per_machine()
