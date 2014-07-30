from alm_user.models import User
from django.test import TestCase
from django.db.utils import IntegrityError


class SimpleTestCase(TestCase):

    def test_user(self):
        u = User(last_name='Kamun')
        self.assertEqual(u.email, '')
