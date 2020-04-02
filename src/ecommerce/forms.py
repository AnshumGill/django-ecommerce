from django import forms
from django.contrib.auth import get_user_model
User=get_user_model()

class ContactForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control","placeholder":"Enter Email"}))
    name=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Name"}))
    content=forms.CharField(widget=forms.Textarea(attrs={"class":"form-control","placeholder":"Your Message"}))
