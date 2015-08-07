from contextlib import contextmanager
from tastypie.authentication import Authentication

from alm_user.models import Account


@contextmanager
def RequestContext(resource, request, allowed_methods=None):
    """Managers lifecycle of tastypie api request"""
    allowed_methods = allowed_methods or []
    resource.method_check(request, allowed=allowed_methods)
    resource.is_authenticated(request)
    resource.throttle_check(request)
    yield
    resource.log_throttled_access(request)


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
