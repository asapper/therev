from django.conf.urls import url

from . import views

app_name = 'control_produccion'
urlpatterns = [
    # ex: /control_produccion/
    url(r'^$', views.ProduccionView.as_view(), name='index'),
    # ex: /control_produccion/orders/
    url(r'^orders/$', views.OrdersView.as_view(), name='orders'),
    # ex: /control_produccion/orders/5/
    url(r'^orders/(?P<pk>[0-9]+)/$', views.OrderDetailView.as_view(),
        name='order_detail'),
]
