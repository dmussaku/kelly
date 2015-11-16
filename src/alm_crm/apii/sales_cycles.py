# -*- coding: utf-8 -*-
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import viewsets

from alm_crm.serializers import SalesCycleSerializer, ActivitySerializer
from alm_crm.models import SalesCycle, Activity

from . import CompanyObjectAPIMixin

class SalesCycleViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = SalesCycleSerializer

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

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, contact=True, latest_activity=True)
            return Response(serializer.data)
        return super(SalesCycleViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='statistics')
    def get_statistics(self, request, *args, **kwargs):
        statistics = SalesCycle.get_statistics(company_id=request.company.id, user_id=request.user.id)
        return Response(statistics)

    @list_route(methods=['get'], url_path='all')
    def get_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_all(company_id=request.company.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='new/all')
    def get_new_all(self, request, *args, **kwargs):	
    	sales_cycles = SalesCycle.get_new_all(company_id=request.company.id)

    	page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='pending/all')
    def get_pending_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_pending_all(company_id=request.company.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='successful/all')
    def get_successful_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_successful_all(company_id=request.company.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='failed/all')
    def get_failed_all(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_failed_all(company_id=request.company.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='my')
    def get_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_my(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='new/my')
    def get_new_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_new_my(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='pending/my')
    def get_pending_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_pending_my(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='successful/my')
    def get_successful_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_successful_my(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='failed/my')
    def get_failed_my(self, request, *args, **kwargs):    
        sales_cycles = SalesCycle.get_failed_my(company_id=request.company.id, user_id=request.user.id)

        page = self.paginate_queryset(sales_cycles)
        if page is not None:
            serializer = self.get_serializer(page, many=True, contact=True, latest_activity=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sales_cycles, many=True, contact=True, latest_activity=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='activities')
    def activities(self, request, *args, **kwargs):
        sales_cycle = self.get_object()
        activities = sales_cycle.rel_activities.all()

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitySerializer(page, many=True, context={'request': request}, sales_cycle=True, contact=True)
            return self.get_paginated_response(serializer.data)

        serializer = ActivitySerializer(activities, many=True, context={'request': request}, sales_cycle=True, contact=True)
        return Response(serializer.data)