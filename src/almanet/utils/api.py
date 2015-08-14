from contextlib import contextmanager


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
