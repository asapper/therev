from django.http import HttpResponse
from django.views import generic


def index(request):
    return HttpResponse("Hello! You're at the Quotes Project index page.")
