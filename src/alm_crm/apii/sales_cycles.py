from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from alm_crm.serializers import SalesCycleSerializer
from alm_crm.models import SalesCycle

from . import CompanyObjectAPIMixin

class SalesCycleViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = SalesCycleSerializer

    def get_serializer(self, *args, **kwargs):
    	serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(contact=True, *args, **kwargs)

    def get_queryset(self):
        return SalesCycle.objects.filter(company_id=self.request.company.id)

    @list_route(methods=['get'], url_path='new/all')
    def get_new_all(self, request, *args, **kwargs):	
    	sales_cycles = SalesCycle.get_new_all(company_id=self.request.company.id)

    	page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True)
        return Response(serializer.data)

