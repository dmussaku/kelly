from rest_framework import serializers

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


class TelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tel
        fields = ('value', 'type',)


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('value', 'type',)


class AdrSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    locality = serializers.CharField(required=False, allow_blank=True)
    country_name = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Adr
        fields = ('street_address', 'region', 'locality', 'country_name','postal_code', 'type',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('data',)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('data',)


class TitleSerializer(serializers.ModelSerializer):
    data = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Title
        fields = ('data',)


class UrlSerializer(serializers.ModelSerializer):
    value = serializers.CharField()
    class Meta:
        model = Url
        fields = ('type', 'value')

    def validate_value(self, value):
        if value.startswith('http://') or value.startswith('https://'):
            return value
        else:
            return 'http://'+value



class VCardSerializer(serializers.ModelSerializer):
    family_name = serializers.CharField(required=False, allow_blank=True)
    given_name = serializers.CharField(required=False, allow_blank=True)
    fn = serializers.CharField(required=False, allow_blank=True)
    tels = TelSerializer(many=True, required=False)
    emails = EmailSerializer(many=True, required=False)
    adrs = AdrSerializer(many=True, required=False)
    categories = CategorySerializer(many=True, required=False)
    notes = NoteSerializer(many=True, required=False)
    titles = TitleSerializer(many=True, required=False)
    urls = UrlSerializer(many=True, required=False)

    class Meta:
        model = VCard
        fields = (
            'id', 
            'fn',
            'family_name',
            'given_name',
            'tels',
            'emails',
            'adrs',
            'categories',
            'notes',
            'titles',
            'urls',
        )

    def create(self, validated_data):
        tels = validated_data.pop('tels', [])
        emails = validated_data.pop('emails', [])
        adrs = validated_data.pop('adrs', [])
        categories = validated_data.pop('categories', [])
        notes = validated_data.pop('notes', [])
        titles = validated_data.pop('titles', [])
        urls = validated_data.pop('urls', [])
        vcard = super(VCardSerializer, self).create(validated_data)
        
        for tel in tels:
            Tel.objects.create(vcard=vcard, **tel)
        for email in emails:
            Email.objects.create(vcard=vcard, **email)
        for adr in adrs:
            Adr.objects.create(vcard=vcard, **adr)
        for category in categories:
            Category.objects.create(vcard=vcard, **category)
        for note in notes:
            Note.objects.create(vcard=vcard, **note)
        for title in titles:
            if title.get('data'):
                Title.objects.create(vcard=vcard, **title)
        for url in urls:
            Url.objects.create(vcard=vcard, **url)
        return vcard
