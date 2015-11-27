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
    	comment = Comment.create_comment(company_id=request.company.id, user_id=request.user.id, data=data)

        serializer = self.get_serializer(comment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)