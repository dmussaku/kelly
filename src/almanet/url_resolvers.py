from urlparse import urlunparse

from django.conf import settings
from django.core.urlresolvers import reverse as django_reverse
from django_hosts.middleware import HostsMiddleware
from django.utils.functional import lazy


def get_domain():
    domain = getattr(settings, 'PARENT_HOST', 'alma.net:8000')
    return domain


def reverse(viewname, subdomain=None, scheme=None,
            args=None, kwargs=None, current_app=None):
    domain = get_domain()
    scheme = scheme or settings.DEFAULT_URL_SCHEME
    if subdomain is not None and subdomain != '':
        domain = '%s.%s' % (subdomain, domain)
    host, _ = HostsMiddleware().get_host(domain)
    urlconf = host.urlconf
    path = django_reverse(
        viewname, urlconf=urlconf, args=args,
        kwargs=kwargs, current_app=current_app) or ''
    return urlunparse((scheme, domain, path, None, None, None))


reverse_lazy = lazy(reverse, str)
