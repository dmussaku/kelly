import functools
from almanet.decorators import subdomain_required, service_required

from django.contrib.auth.decorators import login_required
from django.http import Http404


def crmuser_required(fn):

    @functools.wraps(fn)
    @login_required
    @subdomain_required
    @service_required
    def inner(request, *a, **kw):
        user_id = None
        for subscr_id in request.user_env['subscriptions']:
            subscr_ctx = request.user_env['subscription_%s' % subscr_id]
            if subscr_ctx['slug'] == kw.get('slug', None):
                user_id = subscr_ctx['user_id']
        if user_id is None:
            raise Http404("CRMUser required")
        return fn(request, *a, **kw)
    return inner
