from django.forms import ModelForm

from alm_company.models import Company

class CompanySettingsForm(ModelForm):

    class Meta:
        model = Company
        fields = ['name', 'subdomain']