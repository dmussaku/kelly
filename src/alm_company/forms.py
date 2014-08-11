from django import forms
from django.utils.translation import ugettext_lazy as _
from alm_company.models import Company
from almanet.settings import BUSY_SUBDOMAINS


class CompanySettingsForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['name', 'subdomain']

    def clean_subdomain(self):
        subdomain = self.cleaned_data.get('subdomain', None)
        if subdomain in BUSY_SUBDOMAINS:
            raise forms.ValidationError(_('Cannot take this subdomain'))
        else:
            return subdomain
