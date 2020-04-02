from django.shortcuts import render,redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView
from .forms import MarketingPreferenceForm
from .models import MarketingPreference
# Create your views here.

class MarketingPreferenceUpdateView(SuccessMessageMixin,UpdateView):
    form_class=MarketingPreferenceForm
    template_name='base/marketing-form.html'
    success_url='/settings/email/'
    success_message="Your Email prefrences have been saved. Thank you."

    def dispatch(self,*args,**kwargs):
        user=self.request.user
        if not user.is_authenticated:
            return redirect("/login/?next=/settings/email/")
        return super(MarketingPreferenceUpdateView,self).dispatch(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context=super(MarketingPreferenceUpdateView,self).get_context_data(*args,**kwargs)
        return context

    def get_object(self):
        user=self.request.user
        obj,created=MarketingPreference.objects.get_or_create(user=user)
        return obj
