from django import template
from django.core.exceptions import ObjectDoesNotExist

from ..models import Order_Process


register = template.Library()


@register.simple_tag
def get_process_in_order(order, process):
    """Returns True if Process is associated to Order."""
    try:
        o_proc = Order_Process.objects.get(
            order=order,
            process=process)
    except ObjectDoesNotExist:
        return None
    return o_proc
