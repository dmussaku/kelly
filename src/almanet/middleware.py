import string
import time
import tldextract

from django.contrib.auth import load_backend
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import translation
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date

from alm_company.models import Company
from alm_user.models import Account


class GetSubdomainMiddleware(object):

    def process_request(self, request):
        subdomain = tldextract.extract(
            request.META.get('HTTP_HOST', '')).subdomain or tldextract.extract(
            request.META.get('HTTP_REFERER', '')).subdomain
        if subdomain:
            request.subdomain = subdomain
            request.company = Company.objects.get(subdomain=subdomain)
            if request.user.is_authenticated():
                request.account = get_object_or_404(Account, company_id=request.company.id, user_id=request.user.id)


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
