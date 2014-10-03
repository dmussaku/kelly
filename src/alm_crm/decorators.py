import functools
from .models import CRMUser
from almanet.decorators import subdomain_required, service_required

from django.contrib.auth.decorators import login_required
from django.http import Http404


def crmuser_required(fn):

    @functools.wraps(fn)
    @service_required
    @subdomain_required
    @login_required
    def inner(request, *a, **kw):
        try:
            CRMUser.objects.get(user_id=request.user.pk,
                                organization_id=request.user.company.pk)
        except:
            raise Http404("CRMUser required")
        return fn(request, *a, **kw)
    return inner
