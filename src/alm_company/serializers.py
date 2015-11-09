from rest_framework import serializers


from alm_company.models import Company
from alm_crm.serializers import RequestContextMixin

class CompanySerializer(RequestContextMixin, serializers.ModelSerializer):

    class Meta:
        model = Company