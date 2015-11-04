from rest_framework import serializers

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard

from .models import Milestone, Contact, SalesCycle, Activity, Product, ProductGroup, SalesCycleLogEntry

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


class SalesCycleLogEntrySerializer(RequestContextMixin, serializers.ModelSerializer):
    class Meta:
        model = SalesCycleLogEntry


class SalesCycleSerializer(RequestContextMixin, serializers.ModelSerializer):
    log = SalesCycleLogEntrySerializer(many=True)
    activity_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = SalesCycle

    def __init__(self, *args, **kwargs):
        # pass contact=True param to get fully hydrated contact
        if kwargs.pop('contact', False):
            self.fields['contact'] = ContactSerializer()

        if kwargs.pop('latest_activity', False):
            self.fields['latest_activity'] = serializers.SerializerMethodField()
            
        super(SalesCycleSerializer, self).__init__(*args, **kwargs)

    def get_activity_count(self, obj):
        return obj.rel_activities.filter(deadline__isnull=True).count()

    def get_tasks_count(self, obj):
        return obj.rel_activities.filter(deadline__isnull=False).count()

    def get_latest_activity(self, obj):
        activity = obj.rel_activities.order_by('-date_created').first()
        if activity:
            return ActivitySerializer(activity, context={'request': self.request}).data
        return None


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
