from django_hosts import patterns, host
from django.conf import settings

host_patterns = patterns('',
    host(''.join(['\w+', '\.', settings.HOSTCONF_REGEX]), 'almanet.app_urls', name='apps'),
    host(settings.HOSTCONF_REGEX, settings.ROOT_URLCONF, name='default'),
)