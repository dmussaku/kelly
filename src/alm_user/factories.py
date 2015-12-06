import factory

from django.contrib.auth.hashers import make_password

from alm_company.factories import CompanyFactory

from .models import User, Account

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n : 'user{}@test.com'.format(n))
    password = make_password('123')


class AccountFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Account

	user = factory.SubFactory(UserFactory)
	company = factory.SubFactory(CompanyFactory)