from django.shortcuts import render
import razorpay
client=razorpay.Client(auth=("rzp_test_t7irdtYoVGUAg1","E4MWZEqRizH9aZ291qtKnnLV"))
client.set_app_details({"title" : "Django", "version" : "2.1.3"})
# Create your views here.

def payment_method_view(request):
    if request.method=="POST":
        print(request.POST)
    return render(request,'payment-method.html',{})
