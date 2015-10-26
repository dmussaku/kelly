from django.forms import ModelForm, Form
from django import forms
from django.utils.translation import ugettext_lazy as _
from alm_user.models import Referral


class ReferralForm(Form):
	email = forms.EmailField(label=_("Email"), max_length=254)

	def save(self, commit=True):
		email = self.cleaned_data['email']
		if email:
			referral = Referral(email=email)
			referral.save()
