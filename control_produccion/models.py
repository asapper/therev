from django.db import models


class Process(models.Model):
    # name
    process_name = models.CharField(max_length=100)


class Order(models.Model):
    # OP number
    order_op_number = models.CharField(max_length=10)
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
