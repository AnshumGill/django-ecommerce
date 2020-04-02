from django.db import models
from billing.models import BillingProfile

ADDRESS_TYPE=(
    ('billing','Billing'),
    ('shipping','Shipping'),
)

# Create your models here.
class Address(models.Model):
    billing_profile=models.ForeignKey(BillingProfile,on_delete=models.CASCADE)
    address_type=models.CharField(max_length=120,choices=ADDRESS_TYPE)
    address_line_1=models.CharField(max_length=120)
    address_line_2=models.CharField(max_length=120,null=True,blank=True)
    city=models.CharField(max_length=120)
    state=models.CharField(max_length=100)
    zip_code=models.CharField(max_length=7)

    def __str__(self):
        return str(self.billing_profile)

    def get_address(self):
        return "{line1}\n{line2}\n{city},\n{state}, {zip_code}".format(line1=self.address_line_1,line2=self.address_line_2 or "",city=self.city,state=self.state,zip_code=self.zip_code)
