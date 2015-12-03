import factory

from alm_company.factories import CompanyFactory

from .models import (
    VCard,
    Tel,
    Email,
    Adr,
    Category,
    Note,
    Title,
    Url,
)


class TelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tel

    value = factory.Faker('phone_number')
    type = Tel.TYPE_CHOICES[0][0]


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email

    value = factory.Faker('email')
    type = Email.TYPE_CHOICES[0][0]


class AdrFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Adr

    street_address = factory.Faker('street_address')
    region = factory.Faker('city')
    locality = factory.Faker('state')
    country_name = factory.Faker('country')
    postal_code = factory.Faker('postalcode')
    type = Adr.TYPE_CHOICES[0][0]


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    data = factory.Faker('word')


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    data = factory.Faker('text')


class TitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Title

    data = factory.Faker('job')


class UrlFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Url

    value = factory.Faker('url')
    type = Url.TYPE_CHOICES[0][0]


class VCardFactory(factory.django.DjangoModelFactory):
    fn = factory.Faker('name')
    
    class Meta:
        model = VCard

    @factory.post_generation
    def fill_vcard_fields_in(self, create, extracted, **kwargs):
        if not create:
            return
        for i in range(2):
            TelFactory.create(vcard=self)
        for i in range(3):
            EmailFactory.create(vcard=self)
        for i in range(1):
            AdrFactory.create(vcard=self)
        for i in range(1):
            CategoryFactory.create(vcard=self)
        for i in range(0):
            NoteFactory.create(vcard=self)
        for i in range(1):
            TitleFactory.create(vcard=self)
        for i in range(1):
            UrlFactory.create(vcard=self)
