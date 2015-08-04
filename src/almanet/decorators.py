import functools
from alm_company.models import Company
from almanet.url_resolvers import reverse
from django.conf import settings
from almanet.models import Service
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, Http404


def subdomain_required(fn):

    @functools.wraps(fn)
    def inner(request, *a, **kw):
        if hasattr(request, 'subdomain') and not request.subdomain is None:
            flag = Company.verify_company_by_subdomain(
                request.account.company, request.subdomain)
            if flag:
                return fn(request, *a, **kw)
        messages.warning(request, _("To access this page subdomain required"))
        # redirect_url = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(reverse('user_profile_url', subdomain=settings.MY_SD))

    return inner


def service_required(fn):

    @functools.wraps(fn)
    def inner(request, *a, **kw):
        service_slug = kw.get('service_slug', None)
        try:
            service = Service.objects.get(slug__iexact=service_slug)
        except Service.DoesNotExist:
            raise Http404('Not connected')
        if not request.user.is_service_connected(service):
            raise Http404('Not connected')
        return fn(request, *a, **kw)
    return inner
