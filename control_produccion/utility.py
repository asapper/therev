from django.utils import timezone

from .models import Order_Process, Process


class OrderController():
    @classmethod
    def start_process(cls, order_process_instance):
        """
        Start the given process by caling the Order_Process'
        set_started function.
        """
        # verify order process is not started
        if order_process_instance.get_is_started() is False:
            # function handles assignment
            order_process_instance.set_started()
        else:
            return "Process already started"

    @classmethod
    def finish_process(cls, order_process_instance):
        """
        Finish the given process by calling the Order_Process'
        set_finished function.
        """
        # verify order process is started and not finished
        if order_process_instance.get_is_started() is True:
            if order_process_instance.get_is_finished() is False:
                # function handles assignment
                order_process_instance.set_finished()
            else:
                return "Process already finished"
        else:
            return "Process not started"

    @classmethod
    def get_avg_process_finish_time(cls):
        """
        Return the average time for a Process to be finished.
        """
        # get all processes from Process table
        all_processes = Process.objects.all().order_by('id')
        # store process and average time
        proc_avg_time_list = []
        # get all Order_Process instances related to X process
        for process in all_processes:
            o_processes = Order_Process.objects.filter(process_id=process.id)
            # store duration for all instances of process
            total_duration = 0
            # store number of finished order_processes
            count_finished_processes = 0
            for o_proc in o_processes:
                # if Order_Process if finished
                if o_proc.get_is_finished() is True:
                    # store duration
                    total_duration += o_proc.get_duration()
                    count_finished_processes += 1
            # calculate average time for X process
            if count_finished_processes > 0:
                avg_time = total_duration / count_finished_processes
            else:
                avg_time = 0
            # format average time
            hours, remainder = divmod(avg_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            # store Process-AvgTime in list
            proc_avg_time_list.append(avg_time / 60)
        # return list of processes and their average times
        return proc_avg_time_list

    @classmethod
    def get_process_names(cls):
        """Return the names of all existing processes."""
        # get all processes from Process table
        all_processes = Process.objects.all().order_by('id')
        # store process and average time
        proc_names = []
        # get all Order_Process instances related to X process
        for process in all_processes:
            proc_names.append(process.process_name)
        return proc_names
