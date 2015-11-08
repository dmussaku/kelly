from django.utils import timezone
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from alm_crm.utils import report_builders


class ReportViewSet(viewsets.ViewSet):

    @list_route(methods=['post'], url_path='funnel')
    def funnel(self, request, format=None):
        data = request.data
        report = report_builders.build_funnel(request.company.id, data)
        return Response(report)

    @list_route(methods=['post'], url_path='realtime_funnel')
    def realtime_funnel(self, request, format=None):
        data = request.data
        report = report_builders.build_realtime_funnel(request.company.id, data)
        return Response(report)

    @list_route(methods=['post'], url_path='product_report')
    def product_report(self, request, format=None):
        data = request.data
        report = report_builders.build_product_report(request.company.id, data)
        return Response(report)

    @list_route(methods=['post'], url_path='activity_feed')
    def activity_feed(self, request, format=None):
        data = request.data
        report = report_builders.build_activity_feed(request.company.id, data)
        return Response(report)

    @list_route(methods=['get'], url_path='activity_feed/export')
    def activity_feed_export(self, request, format=None):
        title = force_unicode(_('Activity feed'))
        query_params = request.query_params
        print query_params
        data = {
            'users': query_params.getlist('users', []),
            'date_from': query_params.get('date_from', ''),
            'date_to': query_params.get('date_to', ''),
            'order': query_params.get('order', 'asc'),
            'sort': query_params.get('sort', 'date')
        }
        print data
        xls_file = report_builders.get_activity_feed_xls(request.company.id, data, request.user.timezone.zone)

        response = HttpResponse(xls_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename='+'%s %s.xlsx' % (title, timezone.now().strftime("%d.%m.%y"),)
        try:
            return response
        finally:
            xls_file.close()
