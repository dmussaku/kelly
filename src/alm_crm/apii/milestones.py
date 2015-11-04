from rest_framework import viewsets, permissions

from alm_crm.serializers import MilestoneSerializer
from alm_crm.models import Milestone

from . import CompanyObjectAPIMixin

class MilestoneViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = MilestoneSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Milestone.objects.filter(company_id=self.request.company.id)
