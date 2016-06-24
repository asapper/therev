from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Process(models.Model):
    # name
    process_name = models.CharField(max_length=100)

    def __str__(self):
        """Return a string representation of this Process."""
        return self.process_name

    def get_name(self):
        """Return this Process' name."""
        return self.process_name


class Order(models.Model):
    # OP number
    order_op_number = models.CharField(max_length=10, unique=True)
    # client
    order_client = models.CharField(max_length=255)
    # material description
    order_description = models.CharField(max_length=100)
    # printing machine selected
    order_machine = models.CharField(max_length=50)
    # quantity
    order_quantity = models.PositiveIntegerField()
    # total sheets
    order_total_sheets = models.PositiveSmallIntegerField()
    # processes
    processes = models.ManyToManyField(Process, through="Order_Process")
    # is finished?
    order_is_finished = models.BooleanField(default=False)
    # due date
    order_due_date = models.DateTimeField()
    # date created
    order_date_created = models.DateTimeField()

    def __str__(self):
        """Return a string representation of this Order."""
        return "OP: {}; Cliente: {}; Descripción: {}".format(
            self.order_op_number,
            self.order_client,
            self.order_description)

    def get_op_number(self):
        """Return OP number."""
        return self.order_op_number

    def get_processes(self):
        """Returns this Order's processes."""
        return self.processes.all()

    def get_is_finished(self):
        """Return True if this Order is finished, False otherwise."""
        return self.order_is_finished

    def set_finished(self):
        """Assign this Order's is_finished to True."""
        self.order_is_finished = True
        self.save()

    def get_quantity(self):
        """Returns this Order's quantity."""
        return self.order_quantity

    def is_past_due(self):
        """
        Return True is order was due in the past, return False otherwise.
        """
        return self.order_due_date.date() < timezone.now().date()

    def is_due_today(self):
        """Return True if order is due today, return False otherwise."""
        return self.order_due_date.date() == timezone.now().date()


class Order_Process(models.Model):
    # order reference
    order = models.ForeignKey(Order)
    # process reference
    process = models.ForeignKey(Process)
    # is started?
    order_process_is_started = models.BooleanField(default=False)
    # datetime started
    order_process_datetime_started = models.DateTimeField(null=True)
    # user that started this Order_Process
    order_process_user_started = models.ForeignKey(
        User, related_name='order_processes_started', null=True)
    # is finished?
    order_process_is_finished = models.BooleanField(default=False)
    # datetime finished
    order_process_datetime_finished = models.DateTimeField(null=True)
    # user that finished this Order_Process
    order_process_user_finished = models.ForeignKey(
        User, related_name='order_processes_finished', null=True)
    # datetime process was paused
    order_process_datetime_pause_start = models.DateTimeField(null=True)
    # is paused?
    order_process_is_paused = models.BooleanField(default=False)
    # total seconds paused
    order_process_seconds_paused = models.PositiveIntegerField(default=0)

    def get_op_number(self):
        """Return OP number of associated order."""
        return self.order.get_op_number()

    def get_datetime_started(self):
        """Return the datetime this Order_Process was started."""
        return self.order_process_datetime_started

    def get_is_started(self):
        """Returns True if this Process is started, False otherwise."""
        return self.order_process_is_started

    def set_started(self):
        """
        Assign this Process as started by setting
        its start datetime to timezone.now.
        """
        self.order_process_datetime_started = timezone.now()
        self.order_process_is_started = True
        self.save()

    def get_datetime_finished(self):
        """Return the datetime this Order_Process was finished."""
        return self.order_process_datetime_finished

    def get_is_finished(self):
        """Returns True if this Process is finished, False otherwise."""
        return self.order_process_is_finished

    def set_finished(self):
        """
        Assign this Process as finished by setting
        its start datetime to timezone.now.
        """
        self.order_process_datetime_finished = timezone.now()
        self.order_process_is_finished = True
        self.save()

    def get_is_paused(self):
        """Return the value of is_paused."""
        return self.order_process_is_paused

    def set_paused(self):
        """
        Set is_paued to True, and assign pause_start time to timezone.now.
        """
        self.order_process_datetime_pause_start = timezone.now()
        self.order_process_is_paused = True
        self.save()

    def set_resumed(self):
        """
        Set is_paused to False, and increment seconds_paused by
        timezone.now() - datetime_pause_start. Set pause_start to None.
        """
        diff = timezone.now() - self.order_process_datetime_pause_start
        self.order_process_seconds_paused += diff.total_seconds()
        self.order_process_datetime_pause_start = None
        self.order_process_is_paused = False
        self.save()

    def get_duration(self):
        """Returns the time (in seconds) it took to finish Process."""
        diff = (self.order_process_datetime_finished - 
                self.order_process_datetime_started)
        return diff.total_seconds() - self.order_process_seconds_paused

    def get_order_quantity(self):
        """Returns the quantity stored in associated Order."""
        return self.order.get_quantity()

    def get_process_name(self):
        """Return the name of the associated Process."""
        return self.process.get_name()

    def get_user_who_started_process(self):
        """Return the user who started this Order_Process."""
        return self.order_process_user_started

    def get_user_short_name_who_started_process(self):
        """
        Return the short name of the user who started this Order_Process.
        """
        return self.order_process_user_started.get_short_name()

    def set_user_who_started_process(self, user):
        """Assign the given user to have started this Order_Process."""
        self.order_process_user_started = user
        self.save()

    def get_user_who_finished_process(self):
        """Return the user who finished this Order_Process."""
        return self.order_process_user_finished

    def get_user_short_name_who_finished_process(self):
        """
        Return the short name of the user who finished this Order_Process.
        """
        return self.order_process_user_finished.get_short_name()

    def set_user_who_finished_process(self, user):
        """Assign given user to have finished this Process."""
        self.order_process_user_finished = user
        self.save()
