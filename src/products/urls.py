from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
)

urlpatterns = [
    path('',ProductListView,name="list"),
    path('<int:pk>/',ProductDetailView,name="detailpk"),
    path('<slug:slug>/',ProductDetailView,name="detail"),
]
