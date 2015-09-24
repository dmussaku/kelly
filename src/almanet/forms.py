from django.forms import ModelForm, Form
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Service
from alm_user.models import Referral


class ServiceCreateForm(ModelForm):

	class Meta:
		model = Service
		fields = ['title', 'description']


class ReferralForm(Form):
	email = forms.EmailField(label=_("Email"), max_length=254)

	def save(self, commit=True):
		email = self.cleaned_data['email']
		if email:
			referral = Referral(email=email)
			referral.save()
