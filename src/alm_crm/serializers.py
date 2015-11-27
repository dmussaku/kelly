from rest_framework import serializers

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard
from alm_user.models import User, Account
from alm_company.models import Company

from .models import (
    Milestone, 
    Contact,
    ContactList, 
    SalesCycle, 
    Activity, 
    Product, 
    ProductGroup,
    CustomField,
    SalesCycleLogEntry,
    HashTag,
    Share,
    Notification,
    Filter,
    AttachedFile,
    Comment,
)
from .filters import ContactFilter


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
    children = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Contact.objects.all())

    class Meta:
        model = Contact

    def __init__(self, *args, **kwargs):
        # pass global_sales_cycle=True param to get fully hydrated global_sales_cycle
        if kwargs.pop('global_sales_cycle', False):
            self.fields['global_sales_cycle'] = SalesCycleSerializer()

        # pass parent=True param to get fully hydrated parent
        if kwargs.pop('parent', False):
            self.fields['parent'] = ContactSerializer(global_sales_cycle=True)
        # pass products=True param to get hydrated list of products which are connected to contact
        if kwargs.pop('products', False):
            self.fields['products'] = serializers.SerializerMethodField()

        if kwargs.pop('children', False):
            self.fields['children'] = serializers.SerializerMethodField()

        # pass sales_cycles=True param to get hydrated list of sales cycles
        if kwargs.pop('sales_cycles', False):
            self.fields['sales_cycles'] = SalesCycleSerializer(many=True)
            
        super(ContactSerializer, self).__init__(*args, **kwargs)

    def get_products(self, obj):
        products = obj.get_products()
        if products:
            return ProductSerializer(products, many=True).data
        return []

    def get_children(self, obj):
        return [{child.id: child.vcard.fn} for child in obj.children.all()]


class ContactListSerializer(RequestContextMixin, serializers.ModelSerializer):
    contact_ids = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), many=True, write_only=True, source='contacts')
    contacts = serializers.SerializerMethodField()

    class Meta:
        model = ContactList

    def get_contacts(self, instance):
        return Contact.objects\
            .filter(id__in=instance.contacts.all())\
            .order_by('vcard__fn')\
            .values_list('id', flat=True)


class SalesCycleLogEntrySerializer(RequestContextMixin, serializers.ModelSerializer):
    class Meta:
        model = SalesCycleLogEntry


class SalesCycleSerializer(RequestContextMixin, serializers.ModelSerializer):
    log = SalesCycleLogEntrySerializer(many=True, read_only=True)
    activity_count = serializers.SerializerMethodField(read_only=True)
    tasks_count = serializers.SerializerMethodField(read_only=True)
    real_value = serializers.IntegerField(source='real_value.amount', read_only=True)
    projected_value = serializers.IntegerField(source='projected_value.amount', read_only=True)

    class Meta:
        model = SalesCycle

    def __init__(self, *args, **kwargs):
        # pass contact=True param to get fully hydrated contact
        if kwargs.pop('contact', False):
            self.fields['contact'] = ContactSerializer(read_only=True)

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


class AttachedFileSerializer(RequestContextMixin, serializers.ModelSerializer):
    filename = serializers.CharField(source='file_object.filename', read_only=True)
    swiftfile_id = serializers.IntegerField(source='file_object.id', read_only=True)
    delete = serializers.BooleanField(write_only=True, required=False)
    
    class Meta:
        model = AttachedFile


class ActivitySerializer(RequestContextMixin, serializers.ModelSerializer):
    comments_count = serializers.IntegerField(read_only=True)
    new_comments_count = serializers.SerializerMethodField()
    has_read = serializers.SerializerMethodField()
    sales_cycle_id = serializers.ModelField(model_field=Activity()._meta.get_field('sales_cycle'), write_only=True)
    attached_files = AttachedFileSerializer(many=True, required=False)

    class Meta:
        model = Activity

    def __init__(self, *args, **kwargs):
        # pass contact=True param to get fully hydrated sales_cycle
        if kwargs.pop('sales_cycle', False):
            self.fields['sales_cycle'] = SalesCycleSerializer(contact=kwargs.pop('contact', False), read_only=True)
            
        super(ActivitySerializer, self).__init__(*args, **kwargs)

    def get_new_comments_count(self, obj):
        return obj.new_comments_count(self.request.user.id)

    def get_has_read(self, obj):
        return obj.has_read(user_id=self.request.user.id)


class ProductSerializer(RequestContextMixin, serializers.ModelSerializer):
    stat_value = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        extra_kwargs = {'description': {'required': False}}


class ProductGroupSerializer(RequestContextMixin, serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ProductGroup


class CustomFieldSerializer(RequestContextMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomField


class HashTagSerializer(RequestContextMixin, serializers.ModelSerializer):

    class Meta:
        model = HashTag


class ShareSerializer(RequestContextMixin, serializers.ModelSerializer):
    contact = ContactSerializer()
    
    class Meta:
        model = Share


class NotificationSerializer(RequestContextMixin, serializers.ModelSerializer):
    
    class Meta:
        model = Notification


class FilterSerializer(RequestContextMixin, serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    
    class Meta:
        model = Filter

    def get_count(self, obj):
        return obj.apply(company_id=self.request.company.id, user_id=self.request.user.id).count()


class CommentSerializer(RequestContextMixin, serializers.ModelSerializer):
    
    class Meta:
        model = Comment