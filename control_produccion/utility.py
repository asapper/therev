import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import (Avg, Count, ExpressionWrapper, F,
                              DecimalField)
from django.utils import timezone

from .models import Order, Order_Process, Process


class OrderController():
    @classmethod
    def start_process(cls, order_process_instance, user):
        """
        Start the given process by caling the Order_Process'
        set_started function, and assign the given user
        to have started the given Order_Process.
        """
        # get process name
        process_name = order_process_instance.get_process_name()
        # verify order process is not started
        if order_process_instance.get_is_started() is False:
            # function handles assignment
            order_process_instance.set_started()
            # function handle user assignment
            order_process_instance.set_user_who_started_process(user)
            return messages.SUCCESS, "{} ha sido comenzado!".format(
                process_name)
        else:
            return messages.WARNING, ("{} ha sido comenzado "
                "anteriormente.").format(
                process_name)

    @classmethod
    def pause_all_processes(cls, user):
        """If user is superuser, pause all active processes."""
        if user.is_superuser:
            # get active order process instances
            active_order_processes = Order_Process.objects.filter(
                order_process_is_started=True,
                order_process_is_paused=False,
                order_process_is_finished=False)
            for proc in active_order_processes:
                # handle pausing of process
                cls.pause_process(proc, user)
            return messages.SUCCESS, ("Todos los procesos "
                "activos han sido pausados!")
        else:  # user is not superuser
            return messages.WARNING, ("Usuario {} "
                "no tiene permiso para pausar todos los "
                "procesos").format(user)

    @classmethod
    def pause_process(cls, order_process_instance, user):
        """
        Pause the given process by calling the Order_Process'
        set_paused method.
        """
        # get process name
        process_name = order_process_instance.get_process_name()
        # verify order process is started
        if order_process_instance.get_is_started() is True:
            # verify order process is not finished
            if order_process_instance.get_is_finished() is False:
                # check user who finishes is same as user who started
                user_started = order_process_instance.get_user_who_started_process()
                if user == user_started or user.is_superuser:
                    # function handles assignment
                    order_process_instance.set_paused()
                    return messages.SUCCESS, "{} ha sido pausado!".format(
                        process_name)
                else:  # users do not match
                    return messages.WARNING, ("{} no ha sido pausado! "
                        "Usuario {} no comenzó este proceso.").format(
                            process_name, user)
            else:  # order process is finished
                return messages.WARNING, ("{} no se puede pausar! "
                    "Proceso ya ha sido terminado.").format(
                        process_name)
        else:  # order process is not started
            return messages.WARNING, ("{} no se puede pausar! "
                "Proceso no ha sido comenzado.").format(
                    process_name)

    @classmethod
    def resume_process(cls, order_process_instance, user):
        """
        Resume the given process, if paused, by calling the
        Order_Process' set_resumed method.
        """
        # get process name
        process_name = order_process_instance.get_process_name()
        # verify order process is started
        if order_process_instance.get_is_paused() is True:
            # check user who finishes is same as user who started
            user_started = order_process_instance.get_user_who_started_process()
            if user == user_started or user.is_superuser:
                # function handles assignment
                order_process_instance.set_resumed()
                return messages.SUCCESS, "{} ha sido resumido!".format(
                    process_name)
            else:  # users do not match
                return messages.WARNING, ("{} no ha sido resumido! "
                    "Usuario {} no comenzó este proceso").format(
                    process_name, user)
        else:  # process is not paused
            return messages.WARNING, ("{} no ha sido resumido! "
                "Proceso no ha sido pausado.").format(
                process_name)

    @classmethod
    def finish_process(cls, order_process_instance, user):
        """
        Finish the given process by calling the Order_Process'
        set_finished method, and assign the given user
        to have finished the given Order_Process.
        """
        # get process name
        process_name = order_process_instance.get_process_name()
        # verify order process is started and not finished
        if order_process_instance.get_is_started() is True:
            if order_process_instance.get_is_finished() is False:
                # check user who finishes is same as user who started
                user_started = order_process_instance.get_user_who_started_process()
                if user == user_started or user.is_superuser:
                    # function handles assignment
                    order_process_instance.set_finished()
                    if user.is_superuser:  # superuser finishing a process
                        user = user_started  # assign to user who started it
                    # function handles user assignment
                    order_process_instance.set_user_who_finished_process(user)
                    return messages.SUCCESS, "{} ha sido terminado!".format(
                        process_name)
                else:  # users do not match
                    return messages.WARNING, ("{} no ha sido terminado! "
                        "Usuario {} no comenzó este proceso.").format(
                            process_name, user)
            else:  # order process already finished
                return messages.WARNING, ("{} ha sido terminado "
                    "anteriormente.").format(
                        process_name)
        else:  # order process not started
            return messages.WARNING, ("Proceso no terminado. "
                "{} no ha sido comenzado aún.").format(
                    process_name)

    @classmethod
    def get_avg_process_finish_time(cls):
        """
        Return the average time (minutes) for a Process to be finished
        per unit. The total time is divided by the number of
        copies of the job.
        """
        # get all processes from Process table
        all_processes = Process.objects.all().order_by('id')
        # store process and average time
        proc_avg_time_list = []
        # get all Order_Process instances related to X process
        for process in all_processes:
            o_processes = Order_Process.objects.filter(process_id=process.id)
            # store duration for all instances of process
            total_duration_per_unit = 0
            # store number of finished order_processes
            count_finished_processes = 0
            for o_proc in o_processes:
                # if Order_Process if finished
                if o_proc.get_is_finished() is True:
                    # get quantity
                    quantity = o_proc.get_order_quantity()
                    # store time/unit
                    time_per_unit = (o_proc.get_duration() / 60) / quantity
                    # store duration
                    total_duration_per_unit += time_per_unit
                    count_finished_processes += 1
            # calculate average time for X process
            if count_finished_processes > 0:
                avg_time = total_duration_per_unit / count_finished_processes
            else:
                avg_time = 0
            # store Process-AvgTime in list
            proc_avg_time_list.append((process.process_name, avg_time))
        # sort by avg time
        proc_avg_time_list.sort(key=lambda tup: tup[1], reverse=True)
        # return list of processes and their average times
        return proc_avg_time_list

    @classmethod
    def get_general_top_five_most_often_present_processes(cls):
        """Return the top 5 processes more often present in Orders."""
        return Process.objects.annotate(
            Count('order_process')).order_by('-order_process__count')[:5]

    @classmethod
    def get_last_week_top_five_most_often_present_processes(cls):
        """
        Return the top 5 processes more often present in
        Orders created last week.
        """
        last_week = timezone.now() - datetime.timedelta(days=8)
        return Process.objects.filter(
            order_process__order__order_date_created__gt=last_week).annotate(
                Count('order_process')).order_by('-order_process__count')[:5]

    @classmethod
    def get_last_month_top_five_most_often_present_processes(cls):
        """
        Return the top 5 processes more often present in
        Orders created last month.
        """
        last_month = timezone.now() - datetime.timedelta(days=31)
        return Process.objects.filter(
            order_process__order__order_date_created__gt=last_month).annotate(
                Count('order_process')).order_by('-order_process__count')[:5]

    @classmethod
    def get_general_top_five_most_frequent_clients(cls):
        """Return the top 5 most frequent clients in all Orders."""
        return Order.objects.values('order_client').annotate(
            Count('order_client')).order_by('-order_client__count')[:5]

    @classmethod
    def get_last_week_top_five_most_frequent_clients(cls):
        """
        Return the top 5 most frequent clients in all Orders
        created last week.
        """
        last_week = timezone.now() - datetime.timedelta(days=8)
        return Order.objects.filter(
            order_date_created__gt=last_week).values('order_client').annotate(
                Count('order_client')).order_by('-order_client__count')[:5]

    @classmethod
    def get_last_month_top_five_most_frequent_clients(cls):
        """
        Return the top 5 most frequent clients in all Orders
        created last month.
        """
        last_month = timezone.now() - datetime.timedelta(days=31)
        return Order.objects.filter(
            order_date_created__gt=last_month).values('order_client').annotate(
                Count('order_client')).order_by('-order_client__count')[:5]

    @classmethod
    def get_avg_process_pause_time(cls):
        """
        Return the average time (minutes) that a Process was paused.
        """
        return Order_Process.objects.filter(  # get paused order processes
            order_process_seconds_paused__gt=0).values(  # group by proc name
                'process__process_name').annotate(
                    min_avg_pause=ExpressionWrapper(  # get in minutes
                        Avg(F('order_process_seconds_paused') / 60.0),
                            output_field=DecimalField())).order_by(
                                '-min_avg_pause')

    @classmethod
    def get_workers_processes_finished_and_times(cls):
        """
        Return the number of processes finished per User and
        the average time to finish each of those.
        """
        users = User.objects.all().order_by('first_name')  # get all users
        workers_times = []  # store all data
        for user in users:
            # get all finished Processes by this user
            o_procs = Order_Process.objects.filter(
                order_process_is_finished=True,
                order_process_user_finished=user)
            procs_seen = {}  # keep track of processes seen
            procs_count = {}  # keep track of number of times
            for o_proc in o_procs:
                proc_name = o_proc.get_process_name()
                duration = o_proc.get_duration() / 60  # minutes
                quantity = o_proc.get_order_quantity()
                if proc_name in procs_seen:
                    procs_seen[proc_name] += (duration / quantity)
                    procs_count[proc_name] += 1
                else:
                    procs_seen[proc_name] = (duration / quantity)
                    procs_count[proc_name] = 1
            # store avg time per unit per process for each user
            for proc_name, time in procs_seen.items():
                procs_seen[proc_name] = time/procs_count[proc_name]  # avg
            ordered_procs = list(procs_seen.items())
            ordered_procs.sort(key=lambda tup: tup[0])  # sort by process name
            workers_times.append((user.get_full_name(), ordered_procs))
        return workers_times

    @classmethod
    def get_general_printed_sheets_per_machine(cls):
        """Return the number of printed sheets per machine."""
        return Order.objects.values(  # group by machine
            'order_machine').annotate(
                Count('order_machine'))

    @classmethod
    def get_last_month_printed_sheets_per_machine(cls):
        """
        Return the number of sheets printed in the last 30 days, per machine.
        """
        last_month = timezone.now() - datetime.timedelta(days=31)
        return Order.objects.filter(  # last month's orders
            order_date_created__gt=last_month).values(  # group by machine
                'order_machine').annotate(
                    Count('order_machine'))

    @classmethod
    def get_last_week_printed_sheets_per_machine(cls):
        """
        Return the number of sheets printed in the last 7 days, per machine.
        """
        last_week = timezone.now() - datetime.timedelta(days=8)
        return Order.objects.filter(  # last week's orders
            order_date_created__gt=last_week).values(  # group by machine
                'order_machine').annotate(
                    Count('order_machine'))
