from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status

from alm_crm.models import HashTag

from . import CompanyObjectAPIMixin
from alm_crm.serializers import (
    ContactSerializer,
    ShareSerializer,
    HashTagSerializer
    ) 

class HashTagViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):

    serializer_class = HashTagSerializer

    def get_queryset(self):
        return HashTag.objects.filter(
            company_id=self.request.company.id)