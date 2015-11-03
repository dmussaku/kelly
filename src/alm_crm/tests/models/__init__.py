from alm_user.factories import AccountFactory


class TestMixin(object):
    def set_user(self):
        account = AccountFactory()
        self.company = account.company
        self.user = account.user
