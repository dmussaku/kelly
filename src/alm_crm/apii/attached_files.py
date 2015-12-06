from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets
from almastorage.models import SwiftFile

from alm_crm.serializers import AttachedFileSerializer
from alm_crm.models import AttachedFile

from . import CompanyObjectAPIMixin

CRM_CONTAINER_TITLE = settings.CRM_CONTAINER_TITLE


class AttachedFileViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    serializer_class = AttachedFileSerializer

    def get_queryset(self):
        return AttachedFile.objects.filter(
            company_id=self.request.company.id, owner_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            swiftfile = SwiftFile.upload_file(file_contents=request.FILES['file'],
                                              filename=data['name'], 
                                              content_type=data['type'], 
                                              container_title = CRM_CONTAINER_TITLE,
                                              filesize=data['size'])
        except Exception as e:
            return http.HttpApplicationError(e.message)

        content_class =  ContentType.objects.get(app_label='alm_crm', 
                                                     model=data['content_class'].lower()
                                                    ).model_class()
        content_type = ContentType.objects.get_for_model(content_class)

        attached_file_data = {
            'file_object': swiftfile.id, 
            'content_type': content_type.id,
            'object_id': None,
        }

        serializer = self.get_serializer(data=attached_file_data)
        serializer.is_valid(raise_exception=True)
        attached_file = self.perform_create(serializer)

        return Response({'id': attached_file.id, 
                         'swiftfile_id': swiftfile.id,
                         'filename': data['name'],
                         'delete': False })
