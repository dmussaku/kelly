import tldextract


class GetSubdomainMiddleware(object):

    def process_request(self, request):
        request.subdomain = tldextract.extract(
            request.META['HTTP_HOST']).subdomain


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


class UserEnvMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            request.user_env = {}
            return
        request.user_env = set_user_env(request.user)

