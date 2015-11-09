import dateutil

from rest_framework.decorators import list_route
from rest_framework.response import Response
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

    @list_route(methods=['get'], url_path='statistics')
    def get_statistics(self, request, *args, **kwargs):
        statistics = Activity.get_statistics(company_id=request.company.id, user_id=request.user.id)
        return Response(statistics)

    @list_route(methods=['get'], url_path='company_feed')
    def company_feed(self, request, *args, **kwargs):    
        activities = Activity.company_feed(company_id=request.company.id, user_id=request.user.id)['feed']

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my_feed')
    def my_feed(self, request, *args, **kwargs):    
        activities = Activity.my_feed(company_id=request.company.id, user_id=request.user.id)['feed']

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my_activities')
    def my_activities(self, request, *args, **kwargs):    
        activities = Activity.my_activities(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my_tasks')
    def my_tasks(self, request, *args, **kwargs):    
        activities = Activity.my_tasks(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path='read')
    def mark_as_read(self, request, *args, **kwargs):
        data = request.data
        count = Activity.mark_as_read(company_id=request.company.id, user_id=request.user.id, act_ids=data)
        statistics = Activity.get_statistics(company_id=request.company.id, user_id=request.user.id)

        return Response({
            'count': count,
            'statistics': statistics,
        })

    @list_route(methods=['post'], url_path='calendar')
    def get_calendar(self, request, *args, **kwargs):
        data = request.data
        dt = dateutil.parser.parse(data['dt'])
        calendar_data = Activity.get_calendar(company_id=request.company.id, user_id=request.user.id, dt=dt)
        serializer = self.get_serializer(calendar_data, many=True)

        return Response({
            'calendar_data': serializer.data,
        })
