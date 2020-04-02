from django.contrib import admin
from .models import GuestPhone,EmailActivation
from django.contrib.auth import get_user_model
from .forms import UserAdminChangeForm,UserAdminCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
User=get_user_model()
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('phonenumber', 'full_name', 'admin','is_active')
    list_filter = ('admin','is_active')
    fieldsets = (
        (None, {'fields': ('phonenumber', 'password')}),
        ('Personal info', {'fields': ('full_name','email',)}),
        ('Permissions', {'fields': ('admin','staff','is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phonenumber', 'password1', 'password2')}
        ),
    )
    search_fields = ('phonenumber',)
    ordering = ('phonenumber',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)



# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

User=get_user_model()

class EmailActivationAdmin(admin.ModelAdmin):
    search_fields=['email']
    class Meta:
        model=EmailActivation


admin.site.register(GuestPhone)
admin.site.register(EmailActivation,EmailActivationAdmin)
