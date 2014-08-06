from urlparse import urlunparse

from django.conf import settings
from django.core.urlresolvers import reverse as core_reverse


def get_domain():
    domain = getattr(settings, 'PARENT_HOST', 'almanet.dev')
    return domain

def urljoin(domain, path=None, scheme=None):
    if scheme is None:
        scheme = getattr(settings, 'DEFAULT_URL_SCHEME', 'http')

    return urlunparse((scheme, domain, path or '', None, None, None))


def reverse(viewname, subdomain=None, scheme=None, args=None, kwargs=None,
        current_app=None):
    urlconf = settings.ROOT_URLCONF

    domain = get_domain()
    if subdomain is not None:
        domain = '%s.%s' % (subdomain, domain)

    path = core_reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs,
        current_app=current_app)
    return urljoin(domain, path, scheme=scheme)