import datetime

from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from .models import Order_Process, Process


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
                    time_per_unit = o_proc.get_duration() / quantity
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
