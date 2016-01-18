from django.conf.urls import url

from . import views

app_name = "recursos"
urlpatterns = [
    # ex: /recursos/
    url(r'^$', views.index, name="index"),
    # ex: /recursos/finishings/
    url(r'^finishings/$', views.FinishingsView.as_view(), name='finishings'),
    # ex: /recursos/materials/
    url(r'^materials/$', views.MaterialsView.as_view(), name='materials'),
    # ex: /recursos/papers/
    url(r'^papers/$', views.PapersView.as_view(), name='papers'),
]
