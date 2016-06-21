from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views import generic


def index(request):
    return redirect(reverse('control_produccion:index'))
