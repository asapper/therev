from django.http import HttpResponse
from django.views import generic

from .models import Finishing, Material, Paper


def index(request):
    return HttpResponse("Hello, world. You're at the Recursos index.")


class FinishingsView(generic.ListView):
    template_name = 'recursos/finishings.html'
    context_object_name = 'latest_finishing_list'

    def get_queryset(self):
        """Return all the Finishings."""
        return Finishing.objects.all()


class MaterialsView(generic.ListView):
    template_name = 'recursos/materials.html'
    context_object_name = 'latest_material_list'

    def get_queryset(self):
        """Return all the Finishings."""
        return Material.objects.all()


class PapersView(generic.ListView):
    template_name = 'recursos/papers.html'
    context_object_name = 'latest_paper_list'

    def get_queryset(self):
        """Return all the Finishings."""
        return Paper.objects.all()
