import factory

from .models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('subdomain',)

    name = 'Almacloud'
    subdomain = 'almacloud'