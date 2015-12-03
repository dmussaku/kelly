import factory

from alm_company.factories import CompanyFactory
from alm_vcard.factories import VCardFactory

from .models import (
    Contact,
    Milestone,
    SalesCycle,
    Activity,
    Product,
    ProductGroup,
    Share,
    HashTag,
    HashTagReference,
    SalesCycleProductStat,
    ContactList,
    Filter,
)


class CompanyObjectFactoryMixin(object):
    company = factory.RelatedFactory(CompanyFactory)


class MilestoneFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = Milestone

    title = 'Call'
    

class ContactFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    vcard = factory.SubFactory(VCardFactory)


class SalesCycleFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = SalesCycle

    title = factory.Faker('word')


class ActivityFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    description = factory.Faker('text')


class ProductFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('word')
    price = factory.Faker('pyint')


class ProductGroupFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = ProductGroup

    title = factory.Faker('word')

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for product in extracted:
                self.products.add(product)


class HashTagFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = HashTag

    text = factory.Faker('text')


class HashTagReferenceFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = HashTagReference


class ShareFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = Share

    note = factory.Faker('text')


class SalesCycleProductStatFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = SalesCycleProductStat


class ContactListFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = ContactList

    title = factory.Faker('word')


class FilterFactory(CompanyObjectFactoryMixin, factory.django.DjangoModelFactory):
    class Meta:
        model = Filter

    title = factory.Faker('word')
    filter_text = factory.Faker('word')