from tastypie.authentication import Authentication
from tastypie.utils import trailing_slash
from contextlib import contextmanager
import re


@contextmanager
def RequestContext(resource, request, allowed_methods=None):
    """Managers lifecycle of tastypie api request"""
    allowed_methods = allowed_methods or []
    resource.method_check(request, allowed=allowed_methods)
    resource.is_authenticated(request)
    resource.throttle_check(request)
    yield
    resource.log_throttled_access(request)


class OpenAuthentication(Authentication):

  def is_authenticated(self, request, **kwargs):
    """
    Identifies if the user is authenticated to continue or not.
    Should return either ``True`` if allowed, ``False`` if not or an
    ``HttpResponse`` if you need something custom.
    """
    from alm_crm.api import EmbeddableContactFormResource
    from alm_user.api import UserResource

    auth_endpoint = '/api/v1/%s/auth%s' % (UserResource._meta.resource_name, trailing_slash())
    embeddable_form_endpoint_regex = re.compile('/api/v1/%s/[0-9]+%s' % (EmbeddableContactFormResource._meta.resource_name, trailing_slash()))

    if (request.path == auth_endpoint) or (
      embeddable_form_endpoint_regex.match(request.path) and request.method == 'GET'):
      return True
    return False
