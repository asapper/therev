from django.utils import timezone

from .models import Order, Order_Process


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
