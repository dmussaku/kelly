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

    _company = None
    
    class Meta:
        model = User 


    def get_companies(self, obj):
        return [CompanySerializer(company).data for company in Company.objects.filter(accounts__user_id__in=[obj.id])]

    def get_is_active(self, obj):
        account = obj.accounts.get(
            company_id=self.request.company.id)   
        return account.is_active

    def get_is_supervisor(self, obj):
        account = obj.accounts.get(
            company_id=self.request.company.id)
        return account.is_supervisor

    def get_userpic(self, obj):
        return obj.userpic_obj.url