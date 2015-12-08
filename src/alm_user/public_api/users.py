from django.contrib.auth import login, authenticate

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status

from ..serializers import UserSerializer
from . import PublicAPIMixin


class UserViewSet(PublicAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = UserSerializer
    pagination_class = None


    @list_route(methods=['post'], url_path='auth')
    def authorization(self, request, **kwargs):
        data = request.data

        user = authenticate(
            username=data.get('email'),
            password=data.get('password')
        )
        session_key = None
        session_expire_date = None
        if user is not None:
            if user.is_active:
                login(request, user)  # will add session to request
                session_key = request.session.session_key
                session_expire_date = request.session.get_expiry_date()
            else:
                data = {'message': "User is not activated"}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {'message': "Invalid login"}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        data = {
            'user': self.get_serializer(request.user, context={'request': self.request}).data,
            'session_key': session_key,
            'session_expire_date': session_expire_date
            }

        return Response(data, status=status.HTTP_200_OK)
