from django.conf.urls import url

from . import views

app_name = 'ventas'
urlpatterns = [
    # ex: /ventas/
    url(r'^$', views.VentasView.as_view(), name='index'),
    # ex: /ventas/quotes/
    url(r'^quotes/$', views.QuotesView.as_view(), name='quotes'),
    # ex: /ventas/quotes/new
    url(r'^quotes/new$', views.QuoteCreateView.as_view(),
        name='quote_create'),
    # ex: /ventas/quotes/5/
    url(r'^quotes/(?P<pk>[0-9]+)/$', views.QuoteDetailView.as_view(),
        name='quote_detail'),
    # ex: /ventas/quotes/5/edit/
    url(r'^quotes/(?P<pk>[0-9]+)/edit$', views.QuoteEditView.as_view(),
        name='quote_edit'),
]
