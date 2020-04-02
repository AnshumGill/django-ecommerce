"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView
from addresses.views import checkout_address_create_view,checkout_address_reuse_view
from .views import contact,index,about
from billing.views import payment_method_view
from accounts.views import LoginView,register_page,GuestRegisterView,otp_verification_view
from carts.views import cart_detail_api_view
from marketing.views import MarketingPreferenceUpdateView

urlpatterns = [
    path('',index,name="index"),
    path('contact/',contact,name="contact"),
    path('about/',about,name="about"),
    path('login/',LoginView.as_view(),name="login"),
    path('logout/',LogoutView.as_view(),name="logout"),
    path('register/',register_page,name="register"),
    path('register/guest/',GuestRegisterView.as_view(),name="guest_register"),
    path('otp/',otp_verification_view,name="otp"),
    path('checkout/address/create/',checkout_address_create_view,name="checkout_address_create"),
	path('checkout/address/reuse/',checkout_address_reuse_view,name="checkout_address_reuse"),
    path('payment-method/',payment_method_view,name="payment"),
    path('api/cart/',cart_detail_api_view,name="api-cart"),
    path('products/',include(("products.urls","products"),namespace="products")),
    path('search/',include(("search.urls","search"),namespace="search")),
    path('settings/email/',MarketingPreferenceUpdateView.as_view(),name="marketing-pref"),
    path('settings/',RedirectView.as_view(url='/account')),
    path('accounts/',RedirectView.as_view(url='/account')),
    path('accounts/',include("accounts.passwords.urls")),
    path('cart/',include(("carts.urls","cart"),namespace="cart")),
    path('account/',include(("accounts.urls","accounts"),namespace="account")),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
