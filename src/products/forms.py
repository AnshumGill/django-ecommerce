from django import forms
from .models import Image
PRODUCT_SIZE_CHOICE=(
	(0.5,'½ kg'),
	(1,'1 kg'),
	(1.5,'1½ kg'),
	(2,'2 kg'),
	(2.5,'2½ kg'),
	(3,'3 kg'),
	(4,'4 kg'),
	(5,'5 kg'),
	(10,'10 kg'),
	(20,'20 kg'),
)

class CakeVariationForm(forms.Form):
	size=forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control","placeholder":"Select Size"}),choices=PRODUCT_SIZE_CHOICE,initial=1)
	message=forms.CharField(max_length=120,required=False,widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Cake Message"}))
	

