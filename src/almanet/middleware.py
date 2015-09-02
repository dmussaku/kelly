import string
import time
import tldextract
from django.contrib.auth import load_backend
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date

from alm_company.models import Company

def get_account(request):
    if not hasattr(request, '_cached_account'):
        from alm_user.models import AnonymousAccount
        if not hasattr(request, 'session'):
            account = AnonymousAccount()
        else:
            try:
                account_id = request.session.load()['account_id']
                backend_path = request.session.load()['backend_path']
                assert backend_path in settings.AUTHENTICATION_BACKENDS
                backend = load_backend(backend_path)
                account = backend.get_account(account_id) or AnonymousAccount()
            except (KeyError, AssertionError):
                account = AnonymousAccount()
        request._cached_account = account
    return request._cached_account


class AlmanetSessionMiddleware(object):

    @classmethod
    def create_session(self, request, account):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get('c'+str(account.company_id), None)
        current_session = engine.SessionStore(session_key)
        current_session.flush()
        current_session.update({
            'account_id': account.id,
            'company_id': account.company_id,
            'user_id': account.user_id,
            'backend_path': account.backend,
        })
        current_session.save()
        return current_session

    @classmethod
    def get_session(self, request, cookie_name):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(cookie_name, None)
        return engine.SessionStore(session_key)

    def find_session_for_subdomain(self, subdomain, request):
        engine = import_module(settings.SESSION_ENGINE)
        company = Company.objects.get(subdomain=subdomain)
        session_key = request.COOKIES.get('c'+str(company.id), None)
        return engine.SessionStore(session_key)

    def process_request(self, request):
        if request.META.get('X-User-Agent',"") == 'net.alma.app.mobile' and not request.COOKIES.get('sessionid') and request.META.get('X-Api-Token'):
            api_token = request.META.get('X-Api-Token')
            account = Account.objects.get(key=api_token)
            self.__class__.create_session(request, account)
        engine = import_module(settings.SESSION_ENGINE)
        subdomain = request.subdomain
        session_tokens = request.COOKIES.get('comps', None)
        session_keys = [request.COOKIES.get('c'+session_token, None) for session_token in session_tokens.split(',')] if session_tokens else []
        
        if subdomain != '':
            request.session = self.find_session_for_subdomain(subdomain, request)


    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 500 responses, refs #3881.
                if response.status_code != 500:
                    request.session.save()
                    current_session = request.session.load()

                    comps_cookie = request.COOKIES.get('comps', None)
                    comps = comps_cookie.split(',') if comps_cookie is not None else []

                    if current_session:
                        company = request.account.company

                        
                        comps.append('c'+str(company.id))
                        comps = ','.join(set(comps))

                        response.set_cookie('comps',
                                comps, max_age=max_age,
                                expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                                path=settings.SESSION_COOKIE_PATH,
                                secure=settings.SESSION_COOKIE_SECURE or None,
                                httponly=settings.SESSION_COOKIE_HTTPONLY or None)

                        response.set_cookie('c'+str(company.id),
                                request.session.session_key, max_age=max_age,
                                expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                                path=settings.SESSION_COOKIE_PATH,
                                secure=settings.SESSION_COOKIE_SECURE or None,
                                httponly=settings.SESSION_COOKIE_HTTPONLY or None)
                    else:
                        for comp in comps:
                            cookie = request.COOKIES.get(comp, None)
                            if cookie:
                                session = AlmanetSessionMiddleware.get_session(request, cookie).load()
                                if not session:
                                    response.set_cookie(comp, max_age=0,
                                            expires='Thu, 01-Jan-1970 00:00:00 GMT',
                                            domain=settings.SESSION_COOKIE_DOMAIN,
                                            path=settings.SESSION_COOKIE_PATH,
                                            secure=settings.SESSION_COOKIE_SECURE or None,
                                            httponly=settings.SESSION_COOKIE_HTTPONLY or None)

        return response


class MyAuthenticationMiddleware(object):
    def process_request(self, request):
        # assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.account = SimpleLazyObject(lambda: get_account(request))
        request.company = SimpleLazyObject(lambda: get_account(request).company)
        request.user = SimpleLazyObject(lambda: get_account(request).user or get_account(request)) # set Anonymous if None

class GetSubdomainMiddleware(object):

    def process_request(self, request):
        request.subdomain = tldextract.extract(
            request.META.get('HTTP_HOST', '')).subdomain or tldextract.extract(
            request.META.get('HTTP_REFERER', '')).subdomain


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
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']
