from django.contrib.contenttypes.models import ContentType

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status

from alm_crm.models import Comment
from alm_crm.serializers import CommentSerializer

from . import CompanyObjectAPIMixin


class CommentViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):

    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            company_id=self.request.company.id)

    def create(self, request, *args, **kwargs):
        data = request.data
    	content_class =  ContentType.objects.get(app_label='alm_crm', 
                                                     model=data.pop('content_class').lower()
                                                    ).model_class()
        content_type = ContentType.objects.get_for_model(content_class)
        data['content_type'] = content_type.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)