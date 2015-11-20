from rest_framework import viewsets

from alm_crm.serializers import FilterSerializer
from alm_crm.models import Filter

from . import CompanyObjectAPIMixin


class FilterViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    serializer_class = FilterSerializer
    pagination_class = None

    def get_queryset(self):
        return Filter.objects.filter(
            company_id=self.request.company.id, owner_id=self.request.user.id).order_by('title')
