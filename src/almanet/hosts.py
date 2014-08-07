from django_hosts import patterns, host
from django.conf import settings

SUBDOMAIN_REGEX_PATH = ''.join(['\w+', '\.', settings.HOSTCONF_REGEX])
host_patterns = patterns(
    '',
    host(SUBDOMAIN_REGEX_PATH, 'almanet.app_urls', name='apps'),
    host(settings.HOSTCONF_REGEX, settings.ROOT_URLCONF, name='default'),
)
