import os
import random
from django.db import models
from django.db.models.signals import pre_save
from django.db.models import Q
from django.urls import reverse
from ecommerce.utils import unique_slug_generator
#from PIL import Image as ImagePIL
#from io import BytesIO
#from django.core.files import File
import uuid
# Create your models here.


def get_file_ext(filepath):
    base_name=os.path.basename(filepath)
    name,ext=os.path.splitext(base_name)
    return name,ext

def upload_image_path(instance,filename):
    # new_filename=random.randint(1,34343451)
    # name,ext=get_file_ext(filename)
    # final_filename='{new_filename}{ext}'.format(new_filename=new_filename,ext=ext)
    # return "products/{new_filename}/{final_filename}".format(new_filename=new_filename,final_filename=final_filename)
    if instance.id is not None:
        product_id=instance.id
    else:
        product_id=instance.product_id
    name,ext=get_file_ext(filename)
    new_filename=str(uuid.uuid4()).replace("-","")[:20]
    final_filename='{new_filename}{ext}'.format(new_filename=new_filename,ext=ext)
    return "products/{product_id}/{final_filename}".format(product_id=product_id,final_filename=final_filename)

# def compress(image):
#     img=ImagePIL.open(image)
#     img.thumbnail((1000,1000))
#     im_IO=BytesIO()
#     img.save(im_IO,'JPEG',optimize=True,quality=85)
#     new_image=File(im_IO,name=image.name)
#     return new_image

class ProductQuerySet(models.query.QuerySet):
    def featured(self):
        return self.filter(featured=True)
    def search(self,query):
        lookup =( Q(title__icontains=query) | Q(description__icontains=query) | Q(price__icontains=query) | Q(producttag__title__icontains=query) )
        return self.filter(lookup).distinct()

class ProductManager(models.Manager):
    def get_queryset(self):
        return  ProductQuerySet(self.model,using=self._db)
    def features(self):
        return get.get_queryset().featured()
    def get_by_id(self,id):
        qs=self.get_queryset().filter(id=id)
        if qs.count()==1:
            return qs.first()
        return None
    def search(self,query):
        return self.get_queryset().search(query)

class Products(models.Model):
    title=models.CharField(max_length=120)
    slug=models.SlugField(blank=True,unique=True)
    description=models.TextField()
    price=models.DecimalField(decimal_places=2,max_digits=10,default=0.00)
    image=models.ImageField(upload_to=upload_image_path,null=True,blank=True)
    featured=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    options=models.BooleanField(default=False)
    objects=ProductManager()

    class Meta:
        ordering=['-updated','-timestamp']

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug":self.slug})

    def __str__(self):
        return self.title

class Image(models.Model):
    product=models.ForeignKey(Products,related_name='images',on_delete=models.CASCADE)
    file=models.ImageField(upload_to=upload_image_path,null=True,blank=True)
    timestamp=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-timestamp']


def product_pre_save_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug=unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver,sender=Products)

