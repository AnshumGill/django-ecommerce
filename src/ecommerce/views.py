from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,get_user_model
from .forms import ContactForm
from django.http import JsonResponse,HttpResponse
from products.models import Products
# from instagram.client import InstagramAPI

def index(request):
    context={}
    product_list=Products.objects.filter(featured=True)
    context['products']=product_list
    return render(request,"index.html",context)

def about(request):
    return render(request,"about.html",{})

def contact(request):
    contact_form=ContactForm(request.POST or None)
    context={
        "form":contact_form
    }
    if contact_form.is_valid():
        if request.is_ajax():
            return JsonResponse({"message":"Thank You. We will contact you shortly."})

    if contact_form.errors:
        errors=contact_form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors,status=400,content_type='application/json')

    return render(request,"contact.html",context)

# def instaView(request):
#     clientID="2b3e0856f7564904aa3d5371e82931e7"
#     clientSecret="9b3248d554064387b759b69e845597d5"
#     api = InstagramAPI(client_id=clientID, client_secret=clientSecret)
#     print(api)
#     return render(request,"instagram.html",{})
