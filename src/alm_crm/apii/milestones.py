from rest_framework import viewsets, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from alm_crm.serializers import MilestoneSerializer, SalesCycleSerializer
from alm_crm.models import Milestone
import json

from . import CompanyObjectAPIMixin

class MilestoneViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = MilestoneSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Milestone.objects.filter(company_id=self.request.company.id)

    @list_route(methods=['post'], url_path='bulk_edit')
    def bulk_edit(self, request, *args, **kwargs):
        # data = self.deserialize(
        #     request, request.body,
        #     format=request.META.get('CONTENT_TYPE', 'application/json'))
        data = json.loads(request.data)
        milestones = Milestone.objects.filter(company_id=request.company.id)
        new_milestone_set = []
        max_sort_value = (
            sorted(map(lambda m: m.get('sort',0), data))[-1] or 0)
        for milestone_data in data:
            try:
                milestone = milestones.get(id=milestone_data.get('id', -1))
            except Milestone.DoesNotExist:
                milestone = Milestone()
            else:
                if milestone.title != milestone_data['title'] or \
                   milestone.color_code != milestone_data['color_code'] or \
                   milestone.sort != milestone_data['sort']:
                    for sales_cycle in milestone.sales_cycles.all():
                        sales_cycle.change_milestone(milestone.id, sales_cycle.owner_id, request.company.id)
            finally:
                milestone.title = milestone_data['title']
                milestone.color_code = milestone_data['color_code']
                try:
                    milestone.sort = milestone_data['sort']
                except Exception as e:
                    max_sort_value += 1;
                    milestone.sort = max_sort_value;
                milestone.company_id = request.company.id
                milestone.save()
                new_milestone_set.append(milestone)
        for milestone in milestones:
            if milestone not in new_milestone_set:
                for sales_cycle in milestone.sales_cycles.all():
                    sales_cycle.change_milestone(None, sales_cycle.owner_id, request.company.id)
                milestone.delete()
        bundle = {
            "milestones": [self.serializer_class(milestone).data
                                                        for milestone in new_milestone_set]
        }
        return Response(bundle)

    