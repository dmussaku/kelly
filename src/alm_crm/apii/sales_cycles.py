# -*- coding: utf-8 -*-
import simplejson as json

from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import viewsets, status, filters

from alm_crm.serializers import SalesCycleSerializer, ActivitySerializer
from alm_crm.models import SalesCycle, Activity
from alm_crm.filters import SalesCycleFilter

from . import CompanyObjectAPIMixin

class SalesCycleViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = SalesCycleSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = SalesCycleFilter

    def get_queryset(self):
        return SalesCycle.objects.filter(company_id=self.request.company.id)

    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        # можно передать список айдишников, которые нужно вытащить
        if(query_params.has_key('ids')):
            ids = query_params.get('ids', None).split(',') if query_params.get('ids', None) else []
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.filter(id__in=ids)

            # если передан параметр all, то тогда отдать без pagination'а все циклы
            if(query_params.has_key('all')):
                serializer = self.get_serializer(queryset, many=True, contact=True, latest_activity=True)
                return Response(serializer.data)
            queryset = self.filter_class(request.GET, queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, contact=True, latest_activity=True)
            return Response(serializer.data)
        return super(SalesCycleViewSet, self).list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        '''
        We override this method to ensure that global sales_cycles cannot be deleted through api
        '''
        instance = self.get_object()
        if instance.is_global:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'], url_path='statistics')
    def get_statistics(self, request, *args, **kwargs):
        statistics = SalesCycle.get_statistics(company_id=request.company.id, user_id=request.user.id)
        return Response(statistics)

    @list_route(methods=['get'], url_path='all')
    def get_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_all(company_id=request.company.id).order_by('-latest_activity__date_created', 'date_created')
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='new/all')
    def get_new_all(self, request, *args, **kwargs):	
    	sales_cycles = SalesCycle.get_new_all(company_id=request.company.id).order_by('-date_created')
        sales_cycles = self.filter_class(request.GET, sales_cycles)
    	page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='pending/all')
    def get_pending_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_pending_all(company_id=request.company.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='successful/all')
    def get_successful_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_successful_all(company_id=request.company.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='failed/all')
    def get_failed_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_failed_all(company_id=request.company.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my')
    def get_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_my(company_id=request.company.id, user_id=request.user.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='new/my')
    def get_new_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_new_my(company_id=request.company.id, user_id=request.user.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='pending/my')
    def get_pending_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_pending_my(company_id=request.company.id, user_id=request.user.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='successful/my')
    def get_successful_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_successful_my(company_id=request.company.id, user_id=request.user.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='failed/my')
    def get_failed_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_failed_my(company_id=request.company.id, user_id=request.user.id)
        sales_cycles = self.filter_class(request.GET, sales_cycles)
        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='activities')
    def activities(self, request, *args, **kwargs):
        sales_cycle = self.get_object()
        activities = sales_cycle.rel_activities.order_by('-date_edited')
        
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitySerializer(page, many=True, context={'request': request}, sales_cycle=True, contact=True)
            return self.get_paginated_response(serializer.data)

        serializer = ActivitySerializer(activities, many=True, context={'request': request}, sales_cycle=True, contact=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], url_path='change_milestone')
    def change_milestone(self, request, *args, **kwargs):
        milestone_id = request.data.get('milestone_id')
        sales_cycle = self.get_object()
        sales_cycle = sales_cycle.change_milestone(milestone_id=milestone_id,
                                                   user_id=request.user.id,
                                                   company_id=request.company.id)
        # serializer = self.get_serializer(sales_cycle, contact=True, latest_activity=True)
        serializer = self.get_serializer(sales_cycle)
        return Response(serializer.data)

    @detail_route(methods=['post'], url_path='change_products')
    def change_products(self, request, *args, **kwargs):
        product_ids = request.data.get('product_ids')
        sales_cycle = self.get_object()
        sales_cycle = sales_cycle.change_products(product_ids=product_ids,
                                                  user_id=request.user.id,
                                                  company_id=request.company.id)
        serializer = self.get_serializer(sales_cycle)
        return Response(serializer.data)

    @detail_route(methods=['post'], url_path='succeed')
    def succeed(self, request, *args, **kwargs):
        stats = request.data.get('stats')
        sales_cycle = self.get_object()
        sales_cycle = sales_cycle.succeed(stats=stats,
                                          user_id=request.user.id,
                                          company_id=request.company.id)
        serializer = self.get_serializer(sales_cycle)
        return Response(serializer.data)

    @detail_route(methods=['post'], url_path='fail')
    def fail(self, request, *args, **kwargs):
        stats = request.data.get('stats')
        sales_cycle = self.get_object()
        sales_cycle = sales_cycle.fail(stats=stats,
                                       user_id=request.user.id,
                                       company_id=request.company.id)
        serializer = self.get_serializer(sales_cycle)
        return Response(serializer.data)