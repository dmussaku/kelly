import tldextract


class GetSubdomainMiddleware(object):

    def process_request(self, request):
        request.subdomain = tldextract.extract(
            request.META.get('HTTP_HOST', '')).subdomain


def set_user_env(user):
    env = {'user_id': user.pk}
    subscrs = user.get_subscriptions()
    env['subscriptions'] = map(lambda s: s.pk, subscrs)
    co = user.get_company()
    if co:
        env['company_id'] = co.pk
        env['subdomain'] = co.subdomain
    for subscr in subscrs:
        env['subscription_{}'.format(subscr.pk)] = {
            'is_active': subscr.is_active,
            'user_id': user.get_subscr_user(subscr.pk).pk,
            'slug': subscr.service.slug,
        }
    return env

'''
{% with subscr = request.user_env|get_current_subscription:"id"
  subscr.
'''


class UserEnvMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
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


class XsSharingMiddleware(object):
    """
    This middleware allows cross-domain XHR using the html5 postMessage API.

    Access-Control-Allow-Origin: http://foo.example
    Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE

    Based off https://gist.github.com/426829
    """
    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
            response['Access-Control-Allow-Headers'] = ",".join( XS_SHARING_ALLOWED_HEADERS )
            response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS
            return response

        return None

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
        response['Access-Control-Allow-Headers'] = ",".join( XS_SHARING_ALLOWED_HEADERS )
        response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS

        return response
