from django import forms
from .models import Address
from django.forms import TextInput,NumberInput,Select
STATE_CHOICES=(
    ('Delhi','Delhi'),
    #('Haryana','Haryana'),
)
ZIP_CHOICES=(
    ('110070','110070'),#Vasant Kunj
    ('110057','110057'),#Vasant Vihar
    ('110030','110030'),#Sultanpur, Mehrauli
    ('110067','110067'),#Munirka
    ('110037','110037'),#Mahipalpur
    ('110016','110016'),#Green Park
    ('110074','110074'),#Chattarpur
)

class AddressForm(forms.ModelForm):
    zip_code=forms.ChoiceField(widget=forms.TextInput(attrs={'class':'form-control'}),choices=ZIP_CHOICES,error_messages={'invalid_choice':'Sorry we currently do not deliver in your location. Please contact us for further information.'})
    class Meta:
        model=Address
        fields=[
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'zip_code',
        ]
        
        widgets={
            'address_line_1':TextInput(attrs={'class':'form-control'}),
            'address_line_2':TextInput(attrs={'class':'form-control'}),
            'city':TextInput(attrs={'class':'form-control'}),
            'state':Select(attrs={'class':'form-control'},choices=STATE_CHOICES),
            #'zip_code':Select(attrs={'class':'form-control'},choices=ZIP_CHOICES,error_message={'invalid_choice':'Sorry we currently do not deliver in your location. Please contact us for further information.'})
        }

'''
class AddressForm(forms.Form):
    address_line_1=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    address_line_2=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),required=False)
    city=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    state=forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}),choices=STATE_CHOICES)
    zip_code=forms.ChoiceField(widget=forms.TextInput(attrs={'class':'form-control'}),choices=ZIP_CHOICES,error_messages={'invalid_choice':'Sorry we currently do not deliver in your location. Please contact us for further information.'})
'''