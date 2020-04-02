from django import forms
from django.contrib.auth import get_user_model,authenticate,login
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget,PhoneNumberInternationalFallbackWidget
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import EmailActivation
from .signals import user_logged_in
User=get_user_model()
STATUS=(
    ('ready','Ready'),
    ('out for delivery','Out for Delivery'),
    ('delivered','Delivered'),
)


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phonenumber', 'full_name', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phonenumber', 'full_name', 'email','password', 'is_active', 'admin', 'staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class UserDetailChangeForm(forms.ModelForm):
    full_name=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Enter Name"}),required=False)
    class Meta:
        model=User
        fields=['full_name']

class GuestForm(forms.Form):
    phonenumber=PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget(attrs={"class":"form-control","placeholder":"Phone Number"}))

class otpForm(forms.Form):
    otp=forms.IntegerField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Enter OTP"}))

    def clean(self):
        otp=self.cleaned_data.get("otp")
        if not isinstance(otp,int):
            raise ValidationError("OTP should only contain numbers.")

class loginForm(forms.Form):
    phonenumber=PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget(attrs={"class":"form-control","placeholder":"Phone Number"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}))

    def __init__(self,request,*args,**kwargs):
        self.request=request
        super(loginForm,self).__init__(*args,**kwargs)

    def clean(self):
        request=self.request
        data=self.cleaned_data
        phonenumber=data.get("phonenumber")
        password=data.get("password")
        user = authenticate(request, username=phonenumber, password=password)
        if user is None:
            raise forms.ValidationError("Phone Number and Password do not match. Please try again")
        login(request,user)
        self.user=user
        user_logged_in.send(user.__class__,instance=user,request=request)
        try:
            del request.session['guest_phonenumber_id']
        except:
            pass
        return data

    def clean_phonenumber(self):
        phonenumber=self.cleaned_data.get("phonenumber")
        qs=User.objects.filter(phonenumber=phonenumber)
        if not qs.exists():
            raise forms.ValidationError("Phone Number does not exist")
        return phonenumber


class registerForm(forms.ModelForm):
    """A form for creating new users. Includes all the requiredss
    fields, plus a repeated password."""
    phonenumber=PhoneNumberField(label="Phone Number",widget=PhoneNumberPrefixWidget(attrs={"class":"form-control","placeholder":"Enter Number"}),initial='+91')
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}))
    password2 = forms.CharField(label="PasswordConfirm", widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Confirm Password"}))

    class Meta:
        model = User
        fields = ('full_name', 'email')
        widgets= {
            'full_name':forms.TextInput(attrs={"class":"form-control","placeholder":"Full Name"}),
            'email':forms.EmailInput(attrs={"class":"form-control","placeholder":"Email"}),
        }
        labels= {
            'full_name':"Full Name",
            'email':"Email",
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_phonenumber(self):
        phonenumber=self.cleaned_data.get("phonenumber")
        qs=User.objects.filter(phonenumber=phonenumber)
        if qs.exists():
            raise forms.ValidationError("Number already exists")
        if phonenumber is None:
            raise forms.ValidationError("Please enter a correct Number")
        return phonenumber

    def clean_email(self):
        email=self.cleaned_data.get("email")
        qs=User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email already exists")
        return email

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(registerForm, self).save(commit=False)
        user.phonenumber=self.cleaned_data["phonenumber"]
        user.set_password(self.cleaned_data["password1"])
        user.is_active=False
        
        if commit:
            user.save()
        return user

class statusChangeForm(forms.Form):
    status=forms.ChoiceField(choices=STATUS,widget=forms.RadioSelect(attrs={"class":"form-check-input","type":"radio"}))