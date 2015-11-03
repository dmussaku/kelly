from rest_framework import viewsets

from alm_crm.serializers import ProductSerializer
from alm_crm.models import Product

from . import CompanyObjectAPIMixin

class ProductViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ProductSerializer
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(company_id=self.request.company.id)
