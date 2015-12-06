from rest_framework.decorators import detail_route
from rest_framework.response import Response
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

    @detail_route(methods=['get'], url_path='apply')
    def apply(self, request, *args, **kwargs):
        f = self.get_object()
        data = f.apply(user_id=request.user.id,
                    company_id=request.company.id).qs.values_list('id', flat=True)
        return Response(data)
