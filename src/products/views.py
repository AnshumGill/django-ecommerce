from django.shortcuts import render
from django.http import Http404
from .models import Products,Image
from .forms import CakeVariationForm
from carts.models import Cart
from analytics.signals import object_viewed_signal
# Create your views here.

def ProductListView(request):
    queryset=Products.objects.all()
    images=Image.objects.all()
    context={'object_list':queryset}
    cart_obj,new_obj=Cart.objects.new_or_get(request)
    context['cart']=cart_obj
    return render(request,"product-list.html",context)

def ProductDetailView(request,**kwargs):
    var_form=CakeVariationForm()
    slug=kwargs.get('slug')
    pk=kwargs.get('pk')
    if slug:
        instance=Products.objects.get(slug=slug)
    if pk:
        instance=Products.objects.get_by_id(pk)

    images=Image.objects.filter(product=instance)

    if instance is None:
        raise Http404("Product does not exist")
    #object_viewed_signal.send(sender=instance.__class__,instance=instance,request=request)
    context={'object':instance,'images':images}
    cart_obj,new_obj=Cart.objects.new_or_get(request)
    context['cart']=cart_obj
    context['form']=var_form
    return render(request,"product-detail.html",context)


# def FeaturedListView(request):
#     queryset=Products.objects.all().featured()
#     context={'object_list':queryset}
#     return render(request,"featured-list.html")
#
# def FeaturedDetailView(request,pk,*args,**kwargs):
#     instance=Products.objects.get(pk=pk,featured=True)
#     if instance is None:
#         raise Http404("Product does not exist")
#     context={'object':instance}
#     return render(request,"featured-detail.html",context)
