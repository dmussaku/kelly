import functools
from alm_company.models import Company
from utils import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import HttpResponseRedirect


def subdomain_required(fn):

    @functools.wraps(fn)
    def inner(request, *a, **kw):
        if hasattr(request, 'subdomain') and not request.subdomain is None:
            flag = Company.verify_company_by_subdomain(
                request.user.get_company(), request.subdomain)
            if flag:
                return fn(request, *a, **kw)
        messages.warning(request, _("To access this page subdomain required"))
        redirect_url = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(reverse('user_profile_url'))

    return inner
