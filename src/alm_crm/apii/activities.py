import dateutil
import simplejson as json

from django.db import transaction

from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import viewsets, filters, status

from alm_crm.serializers import (
    ActivitySerializer, 
    NotificationSerializer, 
    SalesCycleSerializer,
    CommentSerializer,
)
from alm_crm.filters import ActivityFilter
from alm_crm.models import Activity, Notification, AttachedFile, Comment
from alm_crm.utils.parser import text_parser

from . import CompanyObjectAPIMixin

class ActivityViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ActivitySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ActivityFilter
    # ordering_fields = '__all__'

    def attach_files(self, attached_files, act_id):
        for file_data in attached_files:
            att_file = AttachedFile.objects.get(id=file_data['id'])
            if file_data.get('delete', False) == False:
                att_file.object_id = act_id
                att_file.save()
            else:
                try: 
                    att_file.delete()
                except:
                    pass

    def get_serializer(self, *args, **kwargs):
    	serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(sales_cycle=True, contact=True, *args, **kwargs)

    def get_queryset(self):
        return Activity.objects.filter(company_id=self.request.company.id).order_by('-date_created')

    def create(self, request, *args, **kwargs):
        data = request.data
        attached_files = data.pop('attached_files', None)

        act = Activity.create_activity(company_id=request.company.id, user_id=request.user.id, data=data)
        
        if(attached_files):
            self.attach_files(attached_files, act.id)

        serializer = self.get_serializer(act)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        attached_files = data.pop('attached_files', None)

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        act = serializer.save()
        text_parser(base_text=act.description, content_class=act.__class__,
                    object_id=act.id, company_id = request.company.id)
        
        if(attached_files):
            self.attach_files(attached_files, act.id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    @list_route(methods=['get'], url_path='statistics')
    def get_statistics(self, request, *args, **kwargs):
        statistics = Activity.get_statistics(company_id=request.company.id, user_id=request.user.id)
        return Response(statistics)

    @list_route(methods=['get'], url_path='company_feed')
    def company_feed(self, request, *args, **kwargs):    
        activities = Activity.company_feed(company_id=request.company.id, user_id=request.user.id)['feed']
        activities = ActivityFilter(request.GET, activities)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my_feed')
    def my_feed(self, request, *args, **kwargs):    
        activities = Activity.my_feed(company_id=request.company.id, user_id=request.user.id)['feed']
        activities = ActivityFilter(request.GET, activities)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='user_activities')
    def user_activities(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id', None) or request.user.id
        activities = Activity.user_activities(company_id=request.company.id, user_id=user_id)
        activities = ActivityFilter(request.GET, activities)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my_tasks')
    def my_tasks(self, request, *args, **kwargs):    
        activities = Activity.my_tasks(company_id=request.company.id, user_id=request.user.id)
        activities = ActivityFilter(request.GET, activities)
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

    @list_route(methods=['post'], url_path='search_by_hashtags')
    def search_by_hashtags(self, request, *args, **kwargs):
        query = request.data.get('q',"").strip()
        activities = Activity.search_by_hashtags(
            company_id=request.company.id, search_query=query)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

        # c = Company.objects.get(subdomain='ordamed')
        # activities = Activity.objects.filter(company_id=c.id)[0:100]
        # for activity in activities:
        #     hash_tag = HashTag(text='#test')
        #     hash_tag.save()
        #     HashTagReference.build_new(
        #         hash_tag.id, 
        #         content_class=Activity, 
        #         object_id=activity.id, 
        #         company_id=c.id, 
        #         save=True)

    @list_route(methods=['post'], url_path='create_multiple')
    def create_multiple(self, request, *args, **kwargs):
        data = request.data
        count = 0

        with transaction.atomic():
            for new_activity_data in data:
                attached_files = new_activity_data.pop('attached_files', None)
                new_activity = Activity.create_activity(company_id=request.company.id, user_id=request.user.id, data=new_activity_data)

                if(attached_files):
                    self.attach_files(attached_files, new_activity.id)
                count+=1

            notification = Notification(
                type='ACTIVITY_CREATION',
                meta=json.dumps({'count': count,}),
                owner=request.user,
                company_id=request.company.id,
            )
            notification.save()

        return Response({'notification': NotificationSerializer(notification).data})

    @detail_route(methods=['post'], url_path='move')
    def move(self, request, *args, **kwargs):
        sales_cycle_id = request.data.get('sales_cycle_id')
        activity = self.get_object()
        rv = activity.move(sales_cycle_id=sales_cycle_id)

        return Response({
            'prev_sales_cycle': SalesCycleSerializer(rv['prev_sales_cycle'], context={'request': request}).data,
            'new_sales_cycle': SalesCycleSerializer(rv['new_sales_cycle'], context={'request': request}).data,
            'activity': self.get_serializer(rv['activity']).data
        })

    @detail_route(methods=['post'], url_path='finish')
    def finish(self, request, *args, **kwargs):
        result = request.data.get('result')
        activity = self.get_object()
        activity = activity.finish(result=result)

        serializer = self.get_serializer(activity)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='comments')
    def comments(self, request, *args, **kwargs):
        activity = self.get_object()
        comments = activity.comments.order_by('date_edited')
        Comment.mark_as_read(company_id=request.company.id, 
                             user_id=request.user.id,
                             comment_ids=comments.values_list('id', flat=True))
        
        activity_serializer = self.get_serializer(activity)
        comments_serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response({
                    'activity': activity_serializer.data,
                    'comments': comments_serializer.data,
                })
