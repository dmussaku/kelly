import simplejson as json

from django.db import transaction

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status, filters

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard
from alm_crm.models import Share, Notification, Contact
from alm_crm.serializers import (
    ShareSerializer,
    NotificationSerializer,
) 
from alm_crm.filters import ShareFilter
from alm_crm.utils.parser import text_parser

from . import CompanyObjectAPIMixin

class ShareViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):

    serializer_class = ShareSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ShareFilter

    def get_queryset(self):
        return Share.objects.filter(
            company_id=self.request.company.id)

    @list_route(methods=['post'], url_path='read')
    def mark_as_read(self, request, *args, **kwargs):
        data = request.data
        count = Share.mark_as_read(company_id=request.company.id, user_id=request.user.id, ids=data)
        statistics = Contact.get_statistics(company_id=request.company.id, user_id=request.user.id)

        return Response({
            'count': count,
            'statistics': statistics,
        })

    @list_route(methods=['post'], url_path='search_by_hashtags')
    def search_by_hashtags(self, request, *args, **kwargs):
        query = request.data.get('q',"").strip()
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
        queryset = ShareFilter(request.GET, shares)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(shares, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path='create_multiple')
    def create_multiple(self, request, *args, **kwargs):
        data = request.data
        count = 0

        with transaction.atomic():
            for new_share_data in data:
                new_share = Share.create_share(company_id=request.company.id, user_id=request.user.id, data=new_share_data)
                text_parser(base_text=new_share.note, content_class=new_share.__class__,
                    object_id=new_share.id, company_id = request.company.id)
                count+=1

            notification = Notification(
                type='SHARE_CREATION',
                meta=json.dumps({'count': count,}),
                owner=request.user,
                company_id=request.company.id,
            )
            notification.save()

        return Response({'notification': NotificationSerializer(notification).data})

