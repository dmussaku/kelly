from contextlib import contextmanager
from django.middleware.csrf import _sanitize_token, constant_time_compare
from tastypie.authentication import Authentication, MultiAuthentication, ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from alm_user.models import Account
from almanet import settings


@contextmanager
def RequestContext(resource, request, auth=True, allowed_methods=None):
    """Managers lifecycle of tastypie api request"""
    allowed_methods = allowed_methods or []
    resource.method_check(request, allowed=allowed_methods)
    if auth:
    	resource.is_authenticated(request)
    resource.throttle_check(request)
    yield
    resource.log_throttled_access(request)


class ApiKeyAuthentication(ApiKeyAuthentication):

    def get_key(self, user, api_key):
        """
        Attempts to find the API key for the user. Uses ``ApiKey`` by default
        but can be overridden.
        """

        try:
            Account.objects.get(user=user, key=api_key)
        except Account.DoesNotExist:
            return self._unauthorized()

        return True


class SessionAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return request.account.is_authenticated()

        if getattr(request, '_dont_enforce_csrf_checks', False):
            return request.account.is_authenticated()

        csrf_token = _sanitize_token(request.COOKIES.get(settings.CSRF_COOKIE_NAME, ''))

        if request.is_secure():
            referer = request.META.get('HTTP_REFERER')

            if referer is None:
                return False

            good_referer = 'https://%s/' % request.get_host()

            if not same_origin(referer, good_referer):
                return False

        request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            return False

        return request.account.is_authenticated()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """

        return getattr(request.account, Account.USERNAME_FIELD)



class DummyPaginator(object):
    def __init__(self, request_data, objects, resource_uri=None,
                 limit=None, offset=0, max_limit=1000,
                 collection_name='objects'):
        self.objects = objects
        self.collection_name = collection_name

    def page(self):
        return {self.collection_name: self.objects}


class CommonMeta:
    list_allowed_methods = ['get', 'post', 'patch']
    detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
    authentication = MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication())
    authorization = Authorization()

    if not settings.RUSTEM_SETTINGS:
        paginator_class = DummyPaginator
    
    filtering = {
        'date_edited': ALL_WITH_RELATIONS
    }

