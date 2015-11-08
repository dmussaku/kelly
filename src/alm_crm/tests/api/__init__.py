import urllib
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

    def prepare_urls(self, path_name, subdomain=None, query={}, *args, **kwargs):
        url = reverse(path_name, subdomain=subdomain, *args, **kwargs)
        url += '?' + urllib.urlencode(query)
        parsed = urlparse(url)
        return url, parsed