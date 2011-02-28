from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^checkout/$', views.checkout, {'typ': 'satchless_cart'}, name='satchless-checkout'),
    url(r'^checkout/delivery_details$', views.delivery_details,
            name='satchless-checkout-delivery_details'),
    url(r'^checkout/payment_choice$', views.payment_choice,
            name='satchless-checkout-payment_choice'),
    )