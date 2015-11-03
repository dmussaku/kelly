from urlparse import urlparse
from almanet.url_resolvers import reverse

from alm_user.factories import AccountFactory


class APITestMixin(object):
    def set_user(self):
        account = AccountFactory()
        self.company = account.company
        self.user = account.user

    def authenticate_user(self):
        self.client.login(email=self.user.email, password='123')

    def prepare_urls(self, path_name, subdomain=None, *args, **kwargs):
        url = reverse(path_name, subdomain=subdomain, *args, **kwargs)
        parsed = urlparse(url)
        return url, parsed