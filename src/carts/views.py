from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Cart
from products.models import Products
from orders.models import Order
from accounts.forms import loginForm,GuestForm
from billing.models import BillingProfile
from accounts.models import GuestPhone
from addresses.forms import AddressForm
from addresses.models import Address
from products.forms import CakeVariationForm
from django.http import QueryDict
import razorpay
client=razorpay.Client(auth=("",""))
client.set_app_details({"title" : "Django", "version" : "2.1.3"})

#"imageUrl":x.image.url

# Create your views here.
def cart_detail_api_view(request):
    cart_obj,new_obj=Cart.objects.new_or_get(request)
    products=[{"name":x.title,"price":x.price} for x in cart_obj.products.all()]
    cart_data={"products":products,"subtotal":cart_obj.subtotal,"total":cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj,new_obj=Cart.objects.new_or_get(request)
    return render(request,"cart-home.html",{'cart':cart_obj})

def cart_update(request):
    product_id=request.POST.get('product_id')
    var_form=CakeVariationForm(request.POST or None)
    add_or_remove=request.POST.get('product_add_or_remove')
    if product_id is not None:
        try:
            product_obj = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            # print("Show message to user, product is gone?")
            return redirect("cart:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            if add_or_remove=='remove':
                cart_obj.variations[product_obj.title]['quantity']-=1
                if cart_obj.variations[product_obj.title]['quantity']<=0:
                    cart_obj.products.remove(product_obj)
                    del cart_obj.variations[product_obj.title]
                added = False
            elif add_or_remove=='add':
                cart_obj.variations[product_obj.title]['quantity']+=1
                added = True
            else:
                cart_obj.products.remove(product_obj)
                del cart_obj.variations[product_obj.title]
                added=False
        else:
            cart_obj.products.add(product_obj)
            cart_obj.variations[product_obj.title]={'quantity':1,'variation':1}
            added = True
        cart_obj.save()
        request.session['cart_items'] = cart_obj.products.count()
        if var_form.is_valid():
            cart_obj.variations[product_obj.title]['variation']=float(var_form.cleaned_data.get("size"))
            cart_obj.variations[product_obj.title]['message']=var_form.cleaned_data.get("message")
            cart_obj.save()
            print(cart_obj.variations)

        if request.is_ajax(): 
            json_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_obj.products.count()
            }
            return JsonResponse(json_data, status=200)

    return redirect("cart:home")


def checkout_home(request):
    cart_obj,cart_created=Cart.objects.new_or_get(request)
    order_obj=None
    if cart_created or cart_obj.products.count()==0:
        return redirect('cart:home')
    login_form=loginForm(request=request)
    guest_form=GuestForm()
    address_form=AddressForm(request.POST or None)
    shipping_address_id=request.session.get("shipping_address_id",None)
    billing_address_id=request.session.get("billing_address_id",None)
    billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)
    address_qs=None
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs=Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created=Order.objects.new_or_get(billing_profile=billing_profile,cart_obj=cart_obj)            
        if shipping_address_id:
            order_obj.shipping_address=Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address=Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if shipping_address_id or billing_address_id:
            order_obj.save()

    context={
        'object':order_obj,
        'billing_profile':billing_profile,
        'login_form':login_form,
        'guest_form':guest_form,
        'address_form':address_form,
        'address_qs':address_qs,
    }
    return render(request,'checkout.html',context)


def checkout_done_view(request):
    if request.method=="POST":
        order_id=request.POST.get('order_id')
        order_obj=Order.objects.get(order_id=order_id)
        paymentid=request.POST.get('payment_id')
        order_obj.payment_id=paymentid
        is_done=order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session['cart_items']=0
            if 'cart_id' in request.session.keys():
                del request.session['cart_id']
        order_obj.save()
        response=client.payment.capture(order_obj.payment_id,int(order_obj.total*100))
    return render(request,'checkout-done.html')
