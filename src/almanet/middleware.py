import tldextract
from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject


class MyAuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.account = SimpleLazyObject(lambda: get_user(request))
        request.user = SimpleLazyObject(lambda: get_user(request) if get_user(request).is_anonymous() else get_user(request).user)



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
        if request.user.is_anonymous() or not request.account.is_authenticated():
            request.user_env = {}
            return
        request.user_env = set_user_env(request.user)


# https://gist.github.com/barrabinfc/426829
from django import http

try:
    from django.conf import settings
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
    XS_SHARING_ALLOWED_HEADERS = settings.XS_SHARING_ALLOWED_HEADERS
    XS_SHARING_ALLOWED_CREDENTIALS = settings.XS_SHARING_ALLOWED_CREDENTIALS
except AttributeError:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
    XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*']
    XS_SHARING_ALLOWED_CREDENTIALS = 'true'


# class XsSharingMiddleware(object):
#     """
#     This middleware allows cross-domain XHR using the html5 postMessage API.

#     Access-Control-Allow-Origin: http://foo.example
#     Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE

#     Based off https://gist.github.com/426829
#     """
#     def process_request(self, request):
#         if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
#             response = http.HttpResponse()
#             response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS
#             response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
#             response['Access-Control-Allow-Headers'] = ",".join( XS_SHARING_ALLOWED_HEADERS )
#             response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS
#             return response

#         return None

#     def process_response(self, request, response):
#         response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS
#         response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
#         response['Access-Control-Allow-Headers'] = ",".join( XS_SHARING_ALLOWED_HEADERS )
#         response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS

#         return response


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
