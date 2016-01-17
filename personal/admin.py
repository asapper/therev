from django.contrib import admin

from .models import Client, Executive, Person

admin.site.register(Client)
admin.site.register(Executive)
admin.site.register(Person)
