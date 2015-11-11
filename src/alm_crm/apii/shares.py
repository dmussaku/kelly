from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status
from alm_crm.models import Share
from alm_crm.serializers import (
    ContactSerializer,
    ShareSerializer
    ) 
from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard
from . import CompanyObjectAPIMixin

class ShareViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):

    serializer_class = ShareSerializer

    def get_queryset(self):
        return Share.objects.filter(
            company_id=self.request.company.id)

    @list_route(methods=['get'], url_path='search_by_hashtags')
    def search_by_hashtags(self, request, *args, **kwargs):
        query = request.GET.get('q',"").strip()
        shares = Share.search_by_hashtags(
            company_id=request.company.id, search_query=query)
        page = self.paginate_queryset(shares)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(shares, many=True)
        return Response(serializer.data)

        # c = Company.objects.get(subdomain='ordamed')
        # shares = Share.objects.filter(company_id=c.id)
        # for share in shares:
        #     hash_tag = HashTag(text='#test')
        #     hash_tag.save()
        #     HashTagReference.build_new(
        #         hash_tag.id, 
        #         content_class=Share, 
        #         object_id=share.id, 
        #         company_id=c.id, 
        #         save=True)
    
    @list_route(methods=['get'], url_path='get_by_user')
    def get_by_user(self, request, *args, **kwargs):    
        shares = Share.get_by_user(
            company_id=request.company.id, user_id=request.user.id)['shares']
        serializer = self.get_serializer(shares, many=True)
        return Response(serializer.data)

