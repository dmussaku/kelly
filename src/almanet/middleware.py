import string
import time
import tldextract
from django.contrib.auth import load_backend
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.http import cookie_date

from alm_company.models import Company


class GetSubdomainMiddleware(object):

    def process_request(self, request):
        subdomain = tldextract.extract(
            request.META.get('HTTP_HOST', '')).subdomain or tldextract.extract(
            request.META.get('HTTP_REFERER', '')).subdomain
        if subdomain:
            request.subdomain = subdomain
            request.company = Company.objects.get(subdomain=subdomain)


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery
    to always choose settings.LANGUAGE_CODE
    as the default initial language, unless
    another one is set via sessions or cookies

    Should be installed *before* any middleware that
    checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """

    def process_request(self, request):
        lang = request.GET.get('lang', None) or request.session.get('lang') or (hasattr(request.user, 'language') and request.user.language)
        if lang:
            translation.activate(lang)
            request.LANGUAGE_CODE = translation.get_language()
            request.META['HTTP_ACCEPT_LANGUAGE'] = lang
            request.session.update({'lang':lang})


from pympler import muppy
from pympler import summary
from pympler import asizeof
from django.conf import settings

import logging


class MemoryMiddleware(object):
    """
    Measure memory taken by requested view, and response
    """
    def _is_media_request(self, request):
        path = request.META['PATH_INFO']
        return "media" in path or (settings.MEDIA_URL and settings.MEDIA_URL in path)

    def process_request(self, request):
        if self._is_media_request(request):
            return None

        self.start_objects = muppy.get_objects()
        
    def process_response(self, request, response):
        if self._is_media_request(request):
            return response
        print 'memory middleware'
        open('example.log', 'w').close()
        logging.basicConfig(filename='example.log',level=logging.INFO)
        path = request.META['PATH_INFO']
        self.end_objects = muppy.get_objects()

        sum_start = summary.summarize(self.start_objects)
        sum_end   = summary.summarize(self.end_objects)
        diff      = summary.get_diff(sum_start, sum_end)

        logging.info("Top 10 memory deltas after processing %s", path)
        print "%-60s %10s %10s" % ("type", "# objects", "total size")
        logging.info("%-60s %10s %10s", "type", "# objects", "total size")

        for row in sorted(diff, key=lambda i: i[2], reverse=True)[:10]:
            print "%60s %10d %10d" % (row[0], row[1], row[2])
            logging.info("%60s %10d %10d", *row)

        start_size = asizeof.asizeof(self.start_objects)
        end_size   = asizeof.asizeof(self.end_objects)

        print ("Processed %s: memory delta %0.1f kB (%0.1f -> %0.1fMB), response size: %0.1f kB" %
            (
                path,
                (end_size - start_size) / 1024.0,
                start_size / 1048576.0,
                end_size / 1048576.0,
                len(response.content)  / 1024.0
            )
        )

        logging.info(
            "Processed %s: memory delta %0.1f kB (%0.1f -> %0.1fMB), response size: %0.1f kB",
            path,
            (end_size - start_size) / 1024.0,
            start_size / 1048576.0,
            end_size / 1048576.0,
            len(response.content)  / 1024.0,
        )

        return respons


from .utils.memory import memory
class SimpleMemoryMiddleware(object):

    def process_request(self, request):
        print memory()
        
    def process_response(self, request, response):
        print memory()
        return response