import base64

from django.contrib.auth import login, authenticate

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status
from almastorage.models import SwiftFile

from almanet.models import Subscription
from alm_vcard.serializers import VCardSerializer
from alm_crm.utils.data_processing import (
    processing_custom_field_data,
)

from ..serializers import UserSerializer
from ..models import User


class UserViewSet(viewsets.ModelViewSet):
    
    serializer_class = UserSerializer
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(
                accounts__company_id__in=[self.request.company.id]
            ).order_by('-date_created')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        # update vcard for user
        vcard = instance.vcard
        custom_fields = data.pop('custom_fields') if data.get('custom_fields') else {}
        if vcard:
            vcard.delete()

        vcard_data = data.pop('vcard')
        vcard_serializer = VCardSerializer(data=vcard_data)
        vcard_serializer.is_valid(raise_exception=True)
        vcard = vcard_serializer.save()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(vcard=vcard)
        if custom_fields:
            processing_custom_field_data(custom_fields, user)
        serializer = self.get_serializer(user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)



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

    @list_route(methods=['post'], url_path='follow_unfollow')
    def follow_unfollow(self, request, **kwargs):
        contact_ids = request.data
        if type(contact_ids) != list:
            return self.create_response(
                request,
                {'success': False, 'message': 'Pass a list as a parameter'}
            )
        request.account.follow_unfollow(contact_ids=contact_ids)

        user = User.objects.get(id=request.user.id)
        return Response(
            self.get_serializer(user, context={'request': self.request}).data)
