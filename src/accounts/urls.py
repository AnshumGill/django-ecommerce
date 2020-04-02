from django.urls import path,re_path
from django.views.decorators.csrf import csrf_exempt
from .views import (
    account_home_view,
    AccountEmailActivateView,
    account_order_view,
    order_detail_view,
    UserDetailUpdateView,
    UserAddressUpdateView,
    adminSite,
    adminSite_order_detail,
)

urlpatterns = [
    path('',account_home_view,name="home"),
    re_path(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$',AccountEmailActivateView.as_view(),name="email-activate"),
    path('orders/',account_order_view,name="order"),
    path('orders/<slug:slug>/',order_detail_view,name="order-detail"),
    path('details/',UserDetailUpdateView.as_view(),name='user-update'),
    path('address/',UserAddressUpdateView,name='user-address'),
    path('admin-manage/',adminSite,name="admin-site"),
    path('admin-manage/<slug:slug>',adminSite_order_detail,name="admin-order"),
]
