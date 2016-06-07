from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.utils import timezone

from . import validators
from recursos.models import Finishing, Material, Paper
from personal.models import Client, Executive


class Quote(models.Model):
    # quote name
    quote_name = models.CharField(max_length=100, unique=True)
    # date created (set it to now when created)
    quote_date_created = models.DateTimeField(auto_now_add=True)
    # date last modified (set it now when modified)
    quote_last_modified = models.DateTimeField(auto_now=True)
    # due date
    quote_due_date = models.DateField(
        validators=[validators.validate_due_date])
    # number of copies
    quote_copies = models.PositiveIntegerField()
    # number of quires
    quote_quires = models.PositiveSmallIntegerField(default=1)
    # product name
    quote_product_name = models.CharField(max_length=100)
    # dimentions (x, y)
    quote_dimention_width = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[validators.validate_dimentions])
    quote_dimention_length = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[validators.validate_dimentions])
    # bleed
    quote_printing_bleed = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0)])
    # printing sides (1 or 2 sides)
    quote_printing_sides = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(2), MinValueValidator(0)])
    # num colors (fron and back)
    quote_printing_colors_front = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(4), MinValueValidator(0)])
    quote_printing_colors_back = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(4), MinValueValidator(0)])
    # is authorized
    quote_is_authorized = models.BooleanField(default=False)
    # datetime authorized
    quote_datetime_authorized = models.DateTimeField(null=True)
    # is approved
    quote_is_approved = models.BooleanField(default=False)
    # total price (set once is approved)
    quote_total_price = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    # imposing per sheet (set once is approved)
    quote_imposing_per_sheet = models.PositiveSmallIntegerField(default=0)
    # total sheets required for job
    quote_total_sheets = models.PositiveIntegerField(default=0)
    # client reference
    client = models.ForeignKey(Client)
    # executive reference
    executive = models.ForeignKey(Executive)
    # finishings reference
    finishings = models.ManyToManyField(Finishing, through='Quote_Finishing')
    # materials reference
    materials = models.ManyToManyField(Material)
    # paper reference
    paper = models.ForeignKey(Paper)

    def __str__(self):
        """Return a string representation of this Quote."""
        return ("Id: {}; Name: {}; Product: {}; Dimentions: {}\" x {}\"; "
                "Due: {}; Copies: {}; Printing sides: {}.").format(
                    self.id,
                    self.quote_name,
                    self.quote_product_name,
                    self.quote_dimention_width,
                    self.quote_dimention_length,
                    self.quote_due_date,
                    self.quote_copies,
                    self.quote_printing_sides)

    def get_quote_id(self):
        """Return this Quote's id."""
        return self.id

    def get_due_date(self):
        """Return this Quote's due date."""
        return self.quote_due_date

    def get_client(self):
        """Return this Quote's client."""
        return self.client

    def get_executive(self):
        """Return this Quote's executive."""
        return self.executive

    def set_executive(self, executive_id):
        """Assign this Quote's executive."""
        self.executive_id = executive_id
        self.save()

    def get_finishings(self):
        """Return this Quote's finishings."""
        return self.finishings.all()

    def set_finishings(self, finishings):
        """Assign new finishings for this Quote. Clear old ones."""
        self.finishings.clear()  # clear old list of finishings
        # store new finishings
        for finishing in finishings:
            Quote_Finishing.objects.create(
                quote=self,
                finishing=finishing)

    def get_materials(self):
        """Return this Quote's materials."""
        return self.materials.all()

    def set_materials(self, materials):
        """Assign new materials for this Quote. Clear old ones."""
        self.materials.set(materials)

    def get_paper(self):
        """Return this Quote's paper."""
        return self.paper

    def set_authorized(self):
        """Set quote_is_authorized to True."""
        self.quote_is_authorized = True
        self.quote_datetime_authorized = timezone.now()
        self.save()

    def set_approved(self):
        """Set quote_is_approved to True."""
        self.quote_is_approved = True
        self.save()

    def set_imposing(self, imposing):
        """Assign the number of imposing per sheet for this Quote."""
        self.quote_imposing_per_sheet = imposing
        self.save()

    def set_total_sheets(self, sheets):
        """Assign the number of sheets used for this Quote."""
        self.quote_total_sheets = sheets
        self.save()

    def set_total_price(self, price):
        """Assign the total price for this Quote."""
        self.quote_total_price = price
        self.save()


class Quote_Finishing(models.Model):
    # quote reference
    quote = models.ForeignKey(Quote)
    # finishing reference
    finishing = models.ForeignKey(Finishing)
    # datetime started
    date_started = models.DateTimeField(null=True)
    # datetime finished
    date_finished = models.DateTimeField(null=True)


class Order(models.Model):
    # auhtorized quote reference
    quote = models.OneToOneField(Quote)
    # date created / quote approved
    order_date_created = models.DateTimeField(auto_now_add=True)
    # packaging instructions
    order_packaging_instructions = models.TextField(null=True)
    # delivery address
    order_delivery_address = models.CharField(max_length=255)
    # notes
    order_notes = models.TextField(null=True)
    # is started?
    order_is_started = models.BooleanField(default=False)
    # datetime started
    order_datetime_started = models.DateTimeField(null=True)
    # is finished?
    order_is_finished = models.BooleanField(default=False)
    # datetime finished
    order_datetime_finished = models.DateTimeField(null=True)

    def __str__(self):
        """Return a string representation of this Order."""
        return "Id: {}; Started: {}; Finished: {}".format(
            self.id, self.order_is_started, self.order_is_finished)

    def get_quote_id(self):
        """Return the quote id associated with this Order."""
        return self.quote.get_quote_id()

    def get_due_date(self):
        """Return the quote due date associated with this Order."""
        return self.quote.get_due_date()

    def get_client(self):
        """Return the client of associated quote."""
        return self.quote.get_client()

    def get_executive(self):
        """Return the executive of associated quote."""
        return self.quote.get_executive()

    def get_finishings(self):
        """Return the finishings of associated quote."""
        return self.quote.get_finishings()

    def get_materials(self):
        """Return the materials of associated quote."""
        return self.quote.get_materials()

    def get_paper(self):
        """Return the paper of associated quote."""
        return self.quote.get_paper()
