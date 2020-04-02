from django.contrib import admin
from .models import Products,Image
#from .forms import MultiImageUpload
# Register your models here.

class ImageAdmin(admin.TabularInline):
	model=Image
	fields=('product','file',)

class ProductAdmin(admin.ModelAdmin):
    list_display=['__str__','slug']
    inlines=[ImageAdmin,]
    class Meta:
        model=Products
        


admin.site.register(Products,ProductAdmin)

