from django.views import generic

from .models import Client, Executive, Person


class PersonalIndexView(generic.base.TemplateView):
    template_name = 'personal/index.html'


class ClientsView(generic.ListView):
    template_name = 'personal/clients.html'
    context_object_name = 'latest_client_list'

    def get_queryset(self):
        """Return all the Clients."""
        return Client.objects.all()


class ExecutivesView(generic.ListView):
    template_name = 'personal/executives.html'
    context_object_name = 'latest_executive_list'

    def get_queryset(self):
        """Return all the Executives."""
        return Executive.objects.all()


class PersonsView(generic.ListView):
    template_name = 'personal/persons.html'
    context_object_name = 'latest_person_list'

    def get_queryset(self):
        """Return all the Persons."""
        return Person.objects.all()
