import functools
from .models import CRMUser
from alm_company.models import Company
from almanet.decorators import subdomain_required, service_required

from django.contrib.auth.decorators import login_required
from django.http import Http404


def crmuser_required(fn):

    @functools.wraps(fn)
    @login_required
    @subdomain_required
    @service_required
    def inner(request, *a, **kw):
        try:
            CRMUser.objects.get(
                user_id=request.user.pk,
                organization_id=Company.objects.get(subdomain=
                                                    request.subdomain).pk)
        except CRMUser.DoesNotExist:
            raise Http404("CRMUser required")
        return fn(request, *a, **kw)
    return inner
