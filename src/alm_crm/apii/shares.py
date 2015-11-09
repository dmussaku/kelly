from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard

from alm_crm.serializers import ShareSerializer
from alm_crm.models import Share

from . import CompanyObjectAPIMixin


class ShareViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ShareSerializer

    def get_queryset(self):
        return Share.objects.filter(company_id=self.request.company.id)

    @list_route(methods=['get'], url_path='get_by_user')
    def get_by_user(self, request, *args, **kwargs):    
        shares = Share.get_by_user(company_id=request.company.id, user_id=request.user.id)['shares']

        page = self.paginate_queryset(shares)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(shares, many=True)
        return Response(serializer.data)
