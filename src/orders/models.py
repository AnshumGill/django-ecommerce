from django.db import models
from carts.models import Cart
from ecommerce.utils import unique_order_id_generator
from django.db.models.signals import pre_save, post_save
from addresses.models import Address
from math import fsum
from django.urls import reverse
from billing.models import BillingProfile
ORDER_STATUS_CHOICES=(
    ('created','Created'),
    ('paid','Paid'),
    ('ready','Ready'),
    ('shipped','Shipped'),
    ('delivered','Delivered')
)

class OrderManager(models.Manager):
    def new_or_get(self,billing_profile,cart_obj):
        new_obj=False
        qs=self.get_queryset().filter(cart=cart_obj,billing_profile=billing_profile,active=True,status="created")
        if qs.count()==1:
            obj=qs.first()
        else:
            obj=self.model.objects.create(billing_profile=billing_profile,cart=cart_obj)
            new_obj=True
        return obj,new_obj

# Create your models here.
class Order(models.Model):
    billing_profile=models.ForeignKey(BillingProfile,on_delete=models.SET_NULL,null=True,blank=True)
    shipping_address=models.ForeignKey(Address,related_name="shipping_address",on_delete=models.SET_NULL,null=True,blank=True)
    billing_address=models.ForeignKey(Address,related_name="billing_address",on_delete=models.SET_NULL,null=True,blank=True)
    order_id=models.CharField(max_length=120,blank=True)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    status=models.CharField(max_length=120,default="created",choices=ORDER_STATUS_CHOICES)
    shipping_total=models.DecimalField(default=0.00,max_digits=4,decimal_places=2)
    total=models.DecimalField(default=0.00,max_digits=100,decimal_places=2)
    payment_id=models.CharField(max_length=255,blank=True,null=True)
    active=models.BooleanField(default=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    objects=OrderManager()

    class Meta:
        ordering=['-timestamp']

    def __str__(self):
        return self.order_id

    def update_total(self):
        cart_total=self.cart.total
        shipping_total=self.shipping_total
        new_total=fsum([cart_total,shipping_total])
        self.total=new_total
        self.save()
        return new_total

    def check_done(self):
        billing_profile=self.billing_profile
        shipping_address=self.shipping_address
        billing_address=self.billing_address
        payment_id=self.payment_id
        total=self.total
        if billing_profile and shipping_address and billing_address and total > 0:
            return True
        return False

    def mark_paid(self):
        if self.check_done():
            self.status='paid'
            self.save()
        return self.status

    def get_absolute_url(self):
        return reverse("accounts:order-detail", kwargs={"slug":self.order_id})

    def get_absolute_url_admin(self):
        return reverse("accounts:admin-order", kwargs={"slug":self.order_id})


def pre_save_create_order_id(sender,instance,*args,**kwargs):
    if not instance.order_id:
        instance.order_id=unique_order_id_generator(instance)
    order_qs=Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if order_qs.exists():
        order_qs.update(active=False)
pre_save.connect(pre_save_create_order_id,sender=Order)

def post_save_cart_total(sender,instance,created,*args,**kwargs):
    if not created:
        cart_obj=instance
        cart_total=cart_obj.total
        cart_id=cart_obj.id
        qs=Order.objects.filter(cart__id=cart_id)
        if qs.count()==1:
            order_obj=qs.first()
            order_obj.update_total()
post_save.connect(post_save_cart_total,sender=Cart)

def post_save_order(sender,instance,created,*args,**kwargs):
    if created:
        instance.shipping_total=50
        instance.update_total()
post_save.connect(post_save_order,sender=Order)
