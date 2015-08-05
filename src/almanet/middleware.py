import string
import time
import tldextract
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.module_loading import import_by_path

from alm_company.models import Company


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

                    company = request.account.company

                    comps = request.COOKIES.get('comps', None)
                    comps_cookie = comps.split(',') if comps is not None else []
                    comps_cookie.append('c'+str(company.id))
                    comps_cookie = ','.join(set(comps_cookie))

                    response.set_cookie('comps',
                            comps_cookie, max_age=max_age,
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
        return response


class MyAuthenticationMiddleware(object):
    def process_request(self, request):
        # assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        # request.account = SimpleLazyObject(lambda: get_account(request))
        # request.user = SimpleLazyObject(lambda: get_user(request) if get_user(request).is_anonymous() else get_user(request).user)
        pass



class GetSubdomainMiddleware(object):

    def process_request(self, request):
        request.subdomain = tldextract.extract(
            request.META.get('HTTP_HOST', '')).subdomain


def set_user_env(user):
    subscrs = user.get_subscriptions()

    env = {
        'user_id': user.pk,
        'account_ids': [acc.id for acc in user.accounts.all()],
        'subscriptions': map(lambda s: s.pk, subscrs)
    }
    for subscr in subscrs:
        env['subscription_{}'.format(subscr.pk)] = {
            'is_active': subscr.is_active,
            'user_id': user.pk,
            'slug': subscr.service.slug,
        }
    return env

'''
{% with subscr = request.user_env|get_current_subscription:"id"
  subscr.
'''


class UserEnvMiddleware(object):
    def process_request(self, request):
        # if request.user.is_anonymous() or not request.account.is_authenticated():
        #     request.user_env = {}
        #     return
        # request.user_env = set_user_env(request.user)
        pass

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
