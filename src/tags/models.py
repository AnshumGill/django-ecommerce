from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from ecommerce.utils import unique_slug_generator
from products.models import Products
# Create your models here.
class ProductTag(models.Model):
    title=models.CharField(max_length=200)
    slug=models.SlugField(blank=True,unique=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    products=models.ManyToManyField(Products,blank=True)

    def __str__(self):
        return self.title

def tag_pre_save_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug=unique_slug_generator(instance)

pre_save.connect(tag_pre_save_receiver,sender=ProductTag)
