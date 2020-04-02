from django.db import models
from django.conf import settings
from django.db.models.signals import post_save,pre_save
from accounts.models import GuestPhone
from phonenumber_field.modelfields import PhoneNumberField
import razorpay
client=razorpay.Client(auth=("rzp_test_t7irdtYoVGUAg1","E4MWZEqRizH9aZ291qtKnnLV"))
client.set_app_details({"title" : "Django", "version" : "2.1.3"})
User=settings.AUTH_USER_MODEL

# Create your models here.
class BillingProfileManager(models.Manager):
    def new_or_get(self,request):
        user=request.user
        guest_phonenumber_id=request.session.get('guest_phonenumber_id')
        new_obj=False
        obj=None
        if user.is_authenticated:
            obj,new_obj=self.model.objects.get_or_create(user=user,phonenumber=user.phonenumber)
        elif guest_phonenumber_id is not None:
            guest_phonenumber_obj=GuestPhone.objects.get(id=guest_phonenumber_id)
            obj,new_obj=self.model.objects.get_or_create(phonenumber=guest_phonenumber_obj.phonenumber)
        else:
            pass
        return obj,new_obj


class BillingProfile(models.Model):
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    phonenumber=PhoneNumberField()
    email=models.EmailField()
    full_name=models.CharField(max_length=255)
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    customer_id=models.CharField(max_length=120,null=True,blank=True)
    objects=BillingProfileManager()

    def __str__(self):
        return str(self.phonenumber)

def billing_profile_created_receiver(sender,instance,*args,**kwargs):
    if not instance.customer_id and instance.phonenumber and instance.email:
        data={"email":instance.email,"contact":str(instance.phonenumber),'name':instance.full_name}
        customer=client.customer.create(data=data)
        instance.customer_id=customer['id']

pre_save.connect(billing_profile_created_receiver,sender=BillingProfile)


def user_created_reciever(sender,instance,created,*args,**kwargs):
    if created and instance.phonenumber:
        BillingProfile.objects.get_or_create(user=instance,phonenumber=instance.phonenumber,email=instance.email,full_name=instance.full_name)

post_save.connect(user_created_reciever,sender=User)
