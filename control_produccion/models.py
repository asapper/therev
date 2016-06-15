from django.db import models
from django.utils import timezone


class Process(models.Model):
    # name
    process_name = models.CharField(max_length=100)

    def __str__(self):
        """Return a string representation of this Process."""
        return "Id: {}; Nombre: {}".format(
            self.id, self.process_name)


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

    def __str__(self):
        """Return a string representation of this Order."""
        return "OP: {}; Cliente: {}; Descripción: {}".format(
            self.order_op_number,
            self.order_client,
            self.order_description)

    def get_processes(self):
        """Returns this Order's processes."""
        return self.processes.all()

    def set_finished(self):
        """Assign this Order's is_finished to True."""
        self.order_is_finished = True
        self.save()


class Order_Process(models.Model):
    # order reference
    order = models.ForeignKey(Order)
    # process reference
    process = models.ForeignKey(Process)
    # is started?
    order_process_is_started = models.BooleanField(default=False)
    # datetime started
    order_process_datetime_started = models.DateTimeField(null=True)
    # is finished?
    order_process_is_finished = models.BooleanField(default=False)
    # datetime finished
    order_process_datetime_finished = models.DateTimeField(null=True)

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
