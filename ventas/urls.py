from django.conf.urls import url

from . import views

app_name = 'ventas'
urlpatterns = [
    # ex: /ventas/
    url(r'^$', views.index, name='index'),
    # ex: /ventas/quotes/
    url(r'^quotes/$', views.QuotesView.as_view(), name='quotes'),
    # ex: /ventas/quotes/5/
    url(r'^quotes/(?P<pk>[0-9]+)/$', views.QuoteDetailView.as_view(),
        name='quote_detail'),
]
