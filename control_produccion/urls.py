from django.conf.urls import url

from . import views

app_name = 'control_produccion'
urlpatterns = [
    # ex: /control_produccion/
    url(r'^$', views.ProduccionView.as_view(), name='index'),
    # ex: /control_produccion/analytics/
    url(r'^analytics/$', views.AnalyticsView.as_view(), name='analytics'),
    # ex: /control_produccion/orders/
    url(r'^orders/$', views.OrdersView.as_view(), name='orders'),
    # ex: /control_produccion/active_orders_display/
    url(r'active_orders_display/$', views.ActiveOrdersView.as_view(),
        name='active_orders'),
    # ex: /control_produccion/active_orders_refresh/
    url(r'active_orders_refresh/$', views.ActiveOrdersRefreshView.as_view(),
        name='active_orders_refresh'),
    # ex: /control_produccion/refresh_database/
    url(r'refresh_database/$', views.ActiveOrdersView.refresh_database,
        name='refresh_database'),
    # ex: /control_produccion/orders/5/
    url(r'^orders/(?P<pk>[0-9]+)/$', views.OrderDetailView.as_view(),
        name='order_detail'),
    # ex: /control_produccion/orders/5/start_process/1/
    url(r'^orders/(?P<pk>[0-9]+)/start_process/(?P<process_id>[0-9]+)/$',
        views.OrderDetailView.start_process, name='order_start_process'),
    # ex: /control_produccion/orders/5/finish_process/1/
    url(r'^orders/(?P<pk>[0-9]+)/finish_process/(?P<process_id>[0-9]+)/$',
       views.OrderDetailView.finish_process, name='order_finish_process'),
    # ex: /control_produccion/orders/5/pause_process/1/
    url(r'^orders/(?P<pk>[0-9]+)/pause_process/(?P<process_id>[0-9]+)/$',
        views.OrderDetailView.pause_process, name='order_pause_process'),
    # ex: /control_produccion/orders/5/resume_process/1/
    url(r'^orders/(?P<pk>[0-9]+)/resume_process/(?P<process_id>[0-9]+)/$',
        views.OrderDetailView.resume_process, name='order_resume_process'),
]
