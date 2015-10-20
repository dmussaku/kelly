from rest_framework import permissions
from rest_framework import viewsets

from alm_crm.serializers import MilestoneSerializer
from alm_crm.models import Milestone

class MilestoneViewSet(viewsets.ModelViewSet):
    
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Milestone.objects.filter(company_id=self.request.company.id)
