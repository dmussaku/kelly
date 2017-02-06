from rest_framework import viewsets, permissions
from alm_crm.serializers import NotificationSerializer
from alm_crm.models import Notification

from . import CompanyObjectAPIMixin

class NotificationViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(owner_id=self.request.user.id, company_id=self.request.company.id)

    