from rest_framework import serializers

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard

from alm_user.models import User, Account
from alm_company.models import Company
from alm_crm.serializers import RequestContextMixin
from alm_company.serializers import CompanySerializer

class UserSerializer(RequestContextMixin, serializers.ModelSerializer):

    companies = serializers.SerializerMethodField()
    vcard = VCardSerializer(required=False)
    is_active = serializers.SerializerMethodField()
    is_supervisor = serializers.SerializerMethodField()
    userpic = serializers.SerializerMethodField()
    unfollow_list = serializers.SerializerMethodField()

    class Meta:
        model = User 

    def get_companies(self, obj):
        companies = Company.objects.filter(accounts__user_id=obj.id)
        return CompanySerializer(companies, many=True).data

    def get_is_active(self, obj):
        return self.request.account.is_active

    def get_is_supervisor(self, obj):
        return self.request.account.is_supervisor

    def get_userpic(self, obj):
        return obj.userpic_obj.url

    def get_unfollow_list(self, obj):
        return self.request.account.unfollow_list.all().values_list('id', flat=True)