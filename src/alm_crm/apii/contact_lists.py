from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status, filters

from alm_crm.serializers import ContactListSerializer
from alm_crm.models import ContactList

from . import CompanyObjectAPIMixin


class ContactListViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    serializer_class = ContactListSerializer
    pagination_class = None

    def get_queryset(self):
        return ContactList.objects.filter(
            company_id=self.request.company.id).order_by('title')
