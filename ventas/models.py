from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Quote(models.Model):
    # quote name
    quote_name = models.CharField(max_length=100, unique=True)
    # date created (set it to now when created)
    quote_date_created = models.DateTimeField(auto_now_add=True)
    # date last modified (set it now when modified)
    quote_last_modified = models.DateTimeField(auto_now=True)
    # due date
    quote_due_date = models.DateField()
    # number of copies
    quote_copies = models.IntegerField()
    # product name
    quote_product_name = models.CharField(max_length=100)
    # dimentions (x, y)
    quote_dimention_width = models.DecimalField(
        max_digits=5, decimal_places=2)
    quote_dimention_length = models.DecimalField(
        max_digits=5, decimal_places=2)
    # bleed
    quote_printing_bleed = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0)])
    # printing sides (1 or 2 sides)
    quote_printing_sides = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(2)])
    # num colors (fron and back)
    quote_printing_colors_front = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(4)])
    quote_printing_colors_back = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(4)])
    # is authorized
    quote_is_authorized = models.BooleanField(default=False)
    # is approved
    quote_is_approved = models.BooleanField(default=True)
    # total price (set once is approved)
    quote_total_price = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    # imposing per sheet (set once is approved)
    quote_imposing_per_sheet = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        """Return a string representation of this Quote."""
        return ("Id: {}; Name: {}; Product: {}; Dimentions: {}\" x {}\"\n"
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
