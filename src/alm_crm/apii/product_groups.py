from rest_framework.response import Response
from rest_framework import viewsets, status

from alm_crm.serializers import ProductGroupSerializer
from alm_crm.models import ProductGroup

from . import CompanyObjectAPIMixin

class ProductGroupViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ProductGroupSerializer
    pagination_class = None

    def get_queryset(self):
        return ProductGroup.objects.filter(company_id=self.request.company.id)

    def create(self, request, *args, **kwargs):
    	serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_group = self.perform_create(serializer)

        for product_id in request.data['products']:
        	product_group.products.add(product_id)

        headers = self.get_success_headers(serializer.data)
        serializer = self.get_serializer(product_group)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
