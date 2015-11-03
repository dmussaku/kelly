from rest_framework import viewsets

from alm_crm.serializers import ActivitySerializer
from alm_crm.models import Activity

from . import CompanyObjectAPIMixin

class ActivityViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ActivitySerializer

    def get_serializer(self, *args, **kwargs):
    	serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(sales_cycle=True, contact=True, *args, **kwargs)

    def get_queryset(self):
        return Activity.objects.filter(company_id=self.request.company.id).order_by('-date_created')
