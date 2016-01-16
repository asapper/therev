from django.db import models


class Client(models.Model):
    # name identifier
    client_name = models.CharField(max_length=100, unique=True)
    # name to appear in receipts
    client_receipt_name = models.CharField(max_length=255)
    # address to appear in receipts
    client_receipt_address = models.CharField(max_length=255)
    # unique NIT
    client_nit = models.IntegerField(unique=True)

    def __str__(self):
        """Return a string representation of this Client instance."""
        return "{}".format(self.client_name)


class Person(models.Model):
    # name
    person_name = models.CharField(max_length=100)
    # lastname
    person_lastname = models.CharField(max_length=100)

    def __str__(self):
        """Return a string representation of this Person instance."""
        return "{}, {}".format(
            self.person_lastname,
            self.person_name)


class Executive(models.Model):
    # Person reference
    person_id = models.ForeignKey(Person)
    # percentage of commission
    executive_comssn = models.DecimalField()

    def __str__(self):
        """Return a string representation of this Executive instance."""
        return "{}".format(self.person_id)
