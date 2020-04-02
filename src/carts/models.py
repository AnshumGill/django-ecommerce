from django.db import models
from django.conf import settings
from products.models import Products
from django.db.models.signals import pre_save,m2m_changed
from django.contrib.postgres.fields import JSONField
from django.db.models import Q
User=settings.AUTH_USER_MODEL

# Create your models here.
class CartManager(models.Manager):
    # def get_cart(self,request):
    #     user=request.user
    #     qs=self.objects.all().filter(user=user)
    #     return qs.first()
    def new_or_get(self,request):
        cart_id=request.session.get("cart_id",None)
        user=request.user
        qs=self.get_queryset().filter(id=cart_id)
        if qs.count()==1:
            new_obj=False
            cart_obj=qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user=request.user
                cart_obj.save()
        else:
            new_obj=True
            cart_obj=Cart.objects.new(user=request.user)
            request.session['cart_id']=cart_obj.id
        return cart_obj,new_obj

    def new(self,user=None):
        user_obj=None
        if user is not None:
            if user.is_authenticated:
                user_obj=user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    user=models.ForeignKey(User, null=True,blank=True,on_delete=models.CASCADE)
    products= models.ManyToManyField(Products,blank=True)
    variations=JSONField(default=dict,null=True,blank=True)
    total=models.DecimalField(default=0.00,max_digits=10,decimal_places=2)
    subtotal=models.DecimalField(default=0.00,max_digits=10,decimal_places=2)
    timestamp=models.DateTimeField(auto_now_add=True,null=True)
    updated=models.DateTimeField(auto_now=True,null=True)
    objects=CartManager()

    def __str__(self):
        return str(self.id)

# def m2m_changed_cart_receiver(sender,instance,action,*args,**kwargs):
#     if action=='post_add' or action=='post_clear' or action=='post_remove':
#         products=instance.products.all()
#         total=0
#         for x in products:
#             total+=x.price
#         if instance.subtotal!=total:
#             instance.subtotal=total
#             instance.save()
# m2m_changed.connect(m2m_changed_cart_receiver,sender=Cart.products.through)

def pre_save_total_cart_receiver(sender,instance,*args,**kwargs):
    if instance.id is not None:
        products=instance.products.all()
        total,subtotal=0,0
        for x in products:
            subtotal=float(x.price)*instance.variations[x.title]['variation']
            subtotal=subtotal*instance.variations[x.title]['quantity']
            total+=round(subtotal,1)
        if instance.subtotal!=total:
            instance.subtotal=total
pre_save.connect(pre_save_total_cart_receiver,sender=Cart)


def pre_save_cart_receiver(sender,instance,*args,**kwargs):
    if instance.subtotal>0.00:
        instance.total=int(instance.subtotal)
    else:
        instance.total=0.00
pre_save.connect(pre_save_cart_receiver,sender=Cart)


