from django.conf.urls import url

from . import views

app_name = 'personal'
urlpatterns = [
    # ex: /personal/
    url(r'^$', views.index, name='index'),
    # ex: /personal/clients/
    url(r'^clients/$', views.ClientsView.as_view(), name='clients'),
    # ex: /personal/executives/
    url(r'^executives/$', views.ExecutivesView.as_view(), name='executives'),
    # ex: /personal/persons/
    url(r'^persons/$', views.PersonsView.as_view(), name='persons'),
]
