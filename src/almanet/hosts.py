from django_hosts import patterns, host
from django.conf import settings

SUBDOMAIN_REGEX_PATH = ''.join(['\w+', '\.', settings.HOSTCONF_REGEX])
host_patterns = patterns(
    '',
    host(r'my', 'alm_user.my_urls', name='my'),
    host(SUBDOMAIN_REGEX_PATH, 'almanet.app_urls', name='apps'),
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(settings.HOSTCONF_REGEX, settings.ROOT_URLCONF, name='default'),
)
