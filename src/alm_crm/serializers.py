from rest_framework import serializers

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard

from .models import Milestone, Contact, SalesCycle, Activity, Product, ProductGroup

class RequestContextMixin(object):
    @property
    def request(self):
        return self.context.get('request')


class MilestoneSerializer(RequestContextMixin, serializers.ModelSerializer):
    class Meta:
        model = Milestone


class ContactSerializer(RequestContextMixin, serializers.ModelSerializer):
    vcard = VCardSerializer(required=False)
    sales_cycles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Contact

    def __init__(self, *args, **kwargs):
        # pass global_sales_cycle=True param to get fully hydrated global_sales_cycle
        if kwargs.pop('global_sales_cycle', False):
            self.fields['global_sales_cycle'] = SalesCycleSerializer()

        # pass parent=True param to get fully hydrated parent
        if kwargs.pop('parent', False):
            self.fields['parent'] = ContactSerializer(global_sales_cycle=True)
            
        super(ContactSerializer, self).__init__(*args, **kwargs)


class SalesCycleSerializer(RequestContextMixin, serializers.ModelSerializer):
    class Meta:
        model = SalesCycle

    def __init__(self, *args, **kwargs):
        # pass contact=True param to get fully hydrated contact
        if kwargs.pop('contact', False):
            self.fields['contact'] = ContactSerializer()
            
        super(SalesCycleSerializer, self).__init__(*args, **kwargs)


class ActivitySerializer(RequestContextMixin, serializers.ModelSerializer):
    comments_count = serializers.IntegerField()
    new_comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity

    def __init__(self, *args, **kwargs):
        # pass contact=True param to get fully hydrated sales_cycle
        if kwargs.pop('sales_cycle', False):
            self.fields['sales_cycle'] = SalesCycleSerializer(contact=kwargs.pop('contact', False))
            
        super(ActivitySerializer, self).__init__(*args, **kwargs)

    def get_new_comments_count(self, obj):
        return obj.new_comments_count(self.request.user.id)


class ProductSerializer(RequestContextMixin, serializers.ModelSerializer):
    stat_value = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        extra_kwargs = {'description': {'required': False}}


class ProductGroupSerializer(RequestContextMixin, serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ProductGroup
