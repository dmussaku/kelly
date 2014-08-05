from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy

from alm_company.models import Company
from alm_company.forms import CompanySettingsForm

class CompanySettingsView(UpdateView):
    """
    Company settings view
    """

    model = Company
    form_class = CompanySettingsForm
    success_url = reverse_lazy('user_profile_url')

    def get_object(self, **kwargs):
        return self.request.user.company.all()[0]