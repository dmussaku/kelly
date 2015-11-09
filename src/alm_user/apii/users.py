import dateutil
import base64

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from alm_user.models import User, Account
from alm_company.models import Company
from almanet.models import Subscription
from almastorage.models import SwiftFile

from alm_user.serializers import UserSerializer

from alm_crm.apii import CompanyObjectAPIMixin

class UserViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = UserSerializer
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(
                accounts__company_id__in=[self.request.company.id]
            ).order_by('-date_created')

    @list_route(methods=['post'], url_path='upload_userpic')
    def upload_userpic(self, request, **kwargs):
        data = request.data

        # from django.core.files.uploadedfile import SimpleUploadedFile
        # file_contents = SimpleUploadedFile("%s" %(data['name']), base64.b64decode(data['pic']), content_type='image')
        # request.user.userpic.save(data['name'], file_contents, True)

        user = User.objects.get(id=request.user.id)
        swiftfile = SwiftFile.upload_file(file_contents=base64.b64decode(data['pic']), filename=data['name'], 
                                            content_type='image', container_title='CRM_USERPICS')
        user.userpic_obj = swiftfile
        user.save()
        return Response(
            self.get_serializer(user, context={'request': self.request}).data)

    @list_route(methods=['post'], url_path='change_password')
    def change_password(self, request, **kwargs):
        data = request.data
        old_password = data.get('old_password', None)
        new_password = data.get('new_password', None)
        user = request.user

        if old_password is None or new_password is None:
            self.error_response(request, {}, response_class=http.HttpBadRequest)

        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(
                {
                    'success': True
                }
            )
        else:
            return Response(
                {
                    'success': False,
                    'error_message': "current password is incorrect"
                }
            )
