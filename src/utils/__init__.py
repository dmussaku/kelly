from urlparse import urlunparse

from django.conf import settings
from django.core.urlresolvers import reverse as django_reverse
from django.utils.functional import lazy


def get_domain():
    domain = getattr(settings, 'PARENT_HOST', 'almanet.dev')
    return domain


def reverse(viewname, subdomain=None, scheme=None,
            args=None, kwargs=None, current_app=None):
    urlconf = settings.ROOT_URLCONF
    domain = get_domain()
    if subdomain is not None:
        domain = '%s.%s' % (subdomain, domain)
    path = django_reverse(
        viewname, urlconf=urlconf, args=args,
        kwargs=kwargs, current_app=current_app) or ''
    scheme = scheme or settings.DEFAULT_URL_SCHEME
    return urlunparse((scheme, domain, path, None, None, None))


reverse_lazy = lazy(reverse, str)
