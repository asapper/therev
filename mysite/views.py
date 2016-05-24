from django.views import generic


class MainSiteIndexView(generic.base.TemplateView):
    template_name = 'index.html'
