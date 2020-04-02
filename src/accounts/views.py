from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import CreateView,FormView,View,UpdateView
from django.contrib import messages
from django.http import JsonResponse,HttpResponse
from django.utils.http import is_safe_url
from django.urls import reverse
from django.utils.safestring import mark_safe
from carts.models import Cart
from orders.models import Order
from billing.models import BillingProfile
from addresses.forms import AddressForm
from addresses.models import Address
from ecommerce.mixins import NextURLMixin,RequestFormAttachMixin
from .forms import loginForm,registerForm,GuestForm,otpForm,UserDetailChangeForm,statusChangeForm
from .signals import user_logged_in
from .models import GuestPhone,User,EmailActivation
import requests
TWOFACTOR_API=getattr(settings,'TWOFACTOR_API')

# Create your views here.
@login_required
def account_home_view(request):
    return render(request,"account-home.html",{})

@login_required
def account_order_view(request):
    user=request.user
    cart_dictionary={}
    billing_qs=BillingProfile.objects.filter(user=user)
    order_qs=Order.objects.filter(billing_profile=billing_qs.first())
    return render(request,"orders.html",{'cart':order_qs})

@login_required
def order_detail_view(request,**kwargs):
    order_id=kwargs.get('slug')
    order_qs=Order.objects.filter(order_id=order_id)
    if order_qs:
        instance=order_qs.first()
    else:
        instance=None   
    return render(request,'order-detail.html',{'order':instance})

class UserDetailUpdateView(LoginRequiredMixin,UpdateView):
    form_class=UserDetailChangeForm
    template_name='detail-update.html'
    def get_object(self):
        return self.request.user

    def get_context_data(self,*args,**kwargs):
        context=super(UserDetailUpdateView,self).get_context_data(*args,**kwargs)
        return context

    def get_success_url(self):
        return reverse("account:home")


@login_required
def UserAddressUpdateView(request):
    address_form=AddressForm(request.POST or None)
    billing_user=BillingProfile.objects.get(user=request.user)
    address_qs=Address.objects.filter(billing_profile=billing_user,address_type='shipping').first()
    context={
        'address':address_qs,
        'form':address_form,
    }
    if address_form.is_valid():
        address_qs.address_line_1=address_form.cleaned_data.get("address_line_1")
        if(address_form.cleaned_data.get("address_line_2")):
            address_qs.address_line_2=address_form.cleaned_data.get("address_line_2")
        else:
            address_qs.address_line_2=None
        address_qs.city=address_form.cleaned_data.get("city")
        address_qs.state=address_form.cleaned_data.get("state")
        address_qs.zip_code=address_form.cleaned_data.get("zip_code")
        address_qs.save()
        messages.success(request,"Your new address is saved.",extra_tags='alert-success')
        return redirect("account:home")
    if address_form.errors:
        messages.error(request,"An error occurred",extra_tags='alert-danger')
    return render(request,'address-update.html',context)

@staff_member_required
def adminSite(request):
    order_qs=Order.objects.all()
    return render(request,"admin-site.html",{'orders':order_qs})

@staff_member_required
def adminSite_order_detail(request,**kwargs):
    form=statusChangeForm(request.POST or None)
    order_id=kwargs.get('slug')
    order_qs=Order.objects.filter(order_id=order_id)
    if order_qs:
        instance=order_qs.first()
    else:
        instance=None   
    if form.is_valid():
        status=form.cleaned_data.get('status')
        if instance is not None:
            instance.status=status
            instance.save()
    return render(request,'admin-order-detail.html',{'order':instance,'form':form})

class AccountEmailActivateView(View):
    def get(self,request,key,*args,**kwargs):
        qs=EmailActivation.objects.filter(key=key)
        confirmable_qs=qs.confirmable()
        if confirmable_qs.count()==1:
            obj=confirmable_qs.first()
            obj.activate()
            messages.success(request,"Your email has been confirmed. Please Login",extra_tags='alert-success')
            return redirect("login")
        else:
            activated_qs=qs.filter(activated=True)
            if activated_qs.exists():
                reset_link=reverse("password_reset")
                msg="""Email has already been confirmed. 
                Do you want to <a href="{link}">reset your Password?</a>
                """.format(link=reset_link)
                messages.success(request,mark_safe(msg),extra_tags='alert-success')  
                return redirect("login")
        return render(request,'registration/activation-error.html',{})


class GuestRegisterView(NextURLMixin,FormView):
    form_class=GuestForm
    default_next="/register/"

    def form_invalid(self,form):
        if request.is_ajax():
            return JsonResponse(form.errors,status=400)
        else:
            return redirect(self.default_next)


    def form_valid(self,form):
        request=self.request
        phonenumber=form.cleaned_data.get("phonenumber")
        new_guest_phonenumber=GuestPhone.objects.create(phonenumber=phonenumber)
        request.session['guest_phonenumber_id']=new_guest_phonenumber.id
        request.session['phonenumber']=str(phonenumber)
        request.session['redirect_path']=self.get_next_url()
        return redirect("/otp/")


def register_page(request):
    register_form=registerForm(request.POST or None,auto_id=False)
    context={
        "form":register_form
    }
    if register_form.is_valid():
        request.session['phonenumber']=str(register_form.cleaned_data.get("phonenumber"))
        register_form.save()
        if request.is_ajax():
            return JsonResponse({"message":"Thank You. You can now Login"})

    if register_form.errors:
        error_dict=register_form.errors
        if request.is_ajax():
            return JsonResponse(error_dict,status=400)

    return render(request,"register.html",context)

class LoginView(NextURLMixin,RequestFormAttachMixin,FormView):
    form_class=loginForm
    success_url="/"
    template_name="login.html"
    default_next='/'

    def get_context_data(self,**kwargs):
        context=super(LoginView,self).get_context_data(**kwargs)
        next_path=self.get_next_url()
        context['next_url']=next_path
        return context

    def form_valid(self,form):
        next_path=self.get_next_url()
        return redirect(next_path)

    def form_invalid(self, form):
        response=super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors,status=400)
        else:
            return response


def otp_verification_view(request,redirect_path=None):
    otp_form=otpForm(request.POST or None)
    context={
        "form":otp_form
    }
    user_phone=request.session['phonenumber']
    response_data={}
    if request.method=="GET":
        url="https://2factor.in/API/V1/"+TWOFACTOR_API+"/SMS/"+user_phone+"/AUTOGEN"
        response=requests.request("GET",url)
        data=response.json()
        request.session['otp_session_data']=data["Details"]
        if data['Status']=="Success":
            response_data={'Message':'Success'}
        else:
            response_data={'Message':'Failed'}
    if otp_form.is_valid():
        otp=str(otp_form.cleaned_data.get("otp"))
        url="https://2factor.in/API/V1/"+TWOFACTOR_API+"/SMS/VERIFY/"+request.session['otp_session_data']+"/"+otp
        response=requests.request("GET",url)
        data=response.json()
        if data['Status']=='Success' and data["Details"]=="OTP Matched":
            del request.session['otp_session_data']
            qs=User.objects.filter(phonenumber=user_phone)
            if qs:
                qs.update(is_active=True)
                qs.first().save()
                messages.success(request,"Your account is activated. Please Login.",extra_tags='alert-success')
                return redirect("login")
            else:
                redirect_path=request.session['redirect_path']
                if redirect_path:
                    return redirect(redirect_path)
        else:
            messages.error(request,"OTP entered is invalid. Try Again.",extra_tags='alert-danger')
    return render(request,"base/otp-verification.html",context)


# class RegisterView(CreateView):
#     form_class = registerForm
#     template_name = 'register.html'
#     success_url = '/login/'
#     def form_valid(self,form):
#         response = super().form_valid(form)
#         if self.request.is_ajax():
#             return JsonResponse({"message":"Thank You. You can now Login"})
#         else:
#             return response
#     def form_invalid(self,form):
#         response = super().form_invalid(form)
#         if self.request.is_ajax():
#             return HttpResponse(form.errors,status=400,content_type='application/json')
#         else:
#             return response

# def login_page(request):
#     login_form=loginForm(request=request)
#     context={
#         "form":login_form
#     }
#     next_=request.GET.get('next')
#     next_post=request.POST.get('next')
#     redirect_path=next_ or next_post or None
#     if login_form.is_valid():  
#         if is_safe_url(redirect_path,request.get_host()):
#             return redirect(redirect_path)
#         else:
#             # if request.is_ajax():
#             #     return HttpResponse("Phone Number and Password do not match",status=400,content_type='application/json')
#             return redirect("/")            

#     if login_form.errors:
#         errors=login_form.errors.as_json()
#         if request.is_ajax():
#             return HttpResponse(errors,status=400,content_type='application/json')

#     return render(request,"login.html",context)
