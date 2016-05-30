import datetime

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_due_date(value):
    today = datetime.date.today()
    if value < today:
        raise ValidationError(
            _('Date must be greater than or equal to today.')
        )


def validate_dimentions(value):
    if value <= Decimal(0):
        raise ValidationError(_('This value must be greater than 0.'))
