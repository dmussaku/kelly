from django.views.generic import TemplateView

from alm_company.models import Company

# TODO: this needs to be deleted
class TestView1(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super(TestView1, self).get_context_data(**kwargs)
        ctx['subdomain'] = self.request.subdomain
        ctx['company'] = Company.objects.get(subdomain=self.request.subdomain)
        ctx['user'] = self.request.user
        return ctx

class TestView2(TemplateView):
    pass