from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models.signals import pre_save,post_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField
from ecommerce.utils import random_string_generator,unique_key_generator

DEFAULT_ACTIVATION_DAYS=getattr(settings,'DEFAULT_ACTIVATION_DAYS',7)

class UserManager(BaseUserManager):
    def create_user(self,phonenumber,full_name,email,password,is_active=False,is_staff=False,is_admin=False):
        if not phonenumber:
            raise ValueError("Users must have a Phone Number")
        if not full_name:
            raise ValueError("Users must have a Name")
        if not email:
            raise ValueError("Users must have an Email")
        if not password:
            raise ValueError("Users must have a Password")


        user_obj=self.model()
        user_obj.phonenumber=phonenumber
        user_obj.full_name=full_name
        user_obj.email=self.normalize_email(email)
        user_obj.set_password(password)
        user_obj.set_admin(is_admin)
        user_obj.set_staff(is_staff)
        user_obj.set_is_active(is_active)
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self,phonenumber,full_name,email,password=None):
        user=self.create_user(
            phonenumber,
            full_name,
            email,
            password=password,
            is_active=True,
            is_staff=True,
        )
        return user

    def create_superuser(self,phonenumber,full_name,email,password=None):
        user=self.create_user(
            phonenumber,
            full_name,
            email,
            password=password,
            is_active=True,
            is_staff=True,
            is_admin=True,
        )
        return user



class User(AbstractBaseUser):
    phonenumber=PhoneNumberField(null=False,blank=False,unique=True)
    full_name=models.CharField(max_length=255,blank=True,null=True)
    email=models.EmailField(max_length=255,unique=True)
    is_active=models.BooleanField(default=True)
    staff=models.BooleanField(default=False)
    admin=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD='phonenumber'
    REQUIRED_FIELDS=['full_name','email']

    objects=UserManager()

    def __str__(self):
        return str(self.phonenumber)

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return str(self.email)

    def has_perm(self,perm,obj=None):
        return True

    def has_module_perms(self,perm,obj=None):
        return True

    def set_admin(self,is_admin):
        self.admin=is_admin

    def set_staff(self,is_staff):
        self.staff=is_staff

    def set_is_active(self,is_activated):
        self.is_active=is_activated

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_activated(self):
        return self.is_active


class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now=timezone.now()
        start_range=now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range=now
        return self.filter(activated=False,forced_expired=False).filter(timestamp__gt=start_range,timestamp__lte=end_range)

class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model,using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

class EmailActivation(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    email=models.EmailField()
    key=models.CharField(max_length=120,blank=True,null=True)
    activated=models.BooleanField(default=False)
    forced_expired=models.BooleanField(default=False)
    expires=models.IntegerField(default=7)
    timestamp=models.DateTimeField(auto_now_add=True)
    update=models.DateTimeField(auto_now=True)

    objects=EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs=EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            user=self.user
            user.is_active=True
            user.save()
            self.activated=True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key=None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation_email(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url=getattr(settings,'BASE_URL')
                key_path=reverse("account:email-activate",kwargs={'key':self.key})
                path="{base}{path}".format(base=base_url,path=key_path)
                context={
                    'user':self.user.full_name,
                    'path':path,
                }
                subject="Please verify your email"
                from_email=settings.DEFAULT_FROM_EMAIL
                html_message=render_to_string("registration/emails/verify.html",context)
                message=strip_tags(html_message)
                recipient_list=[self.email]
                sent_mail=send_mail(subject, message,from_email,recipient_list,html_message=html_message,fail_silently=False)
                return sent_mail
        return False

def pre_save_email_activation(sender,instance,*args,**kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key=unique_key_generator(instance)

pre_save.connect(pre_save_email_activation,sender=EmailActivation)

def post_save_user_create_reciever(sender,instance,created,*args,**kwargs):
    if created:
        obj=EmailActivation.objects.create(user=instance,email=instance.email)
        obj.send_activation_email()

post_save.connect(post_save_user_create_reciever,sender=User)

class GuestPhone(models.Model):
    phonenumber=PhoneNumberField()
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.phonenumber)
