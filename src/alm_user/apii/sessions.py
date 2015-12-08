from rest_framework.views import APIView
from rest_framework.response import Response

from almanet.settings import TIME_ZONE
from alm_company.serializers import CompanySerializer


class SessionAPIView(APIView):

    def get(self, request, format=None):
        company = CompanySerializer(request.company).data
        session = {
            'user_id': request.user.pk,
            'language': request.user.language,
            'timezone': TIME_ZONE
        }
        return Response({
            'company': company,
            'session': session,
        })