from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from alm_crm.utils.helpers import get_dashboard, get_active_deals, get_active_contacts
from alm_crm.serializers import MilestoneSerializer
from alm_crm.models import (
    Contact, 
    SalesCycle,
    SalesCycleLogEntry, 
    HashTag, 
    Share,
    Activity,
    ActivityRecipient,
)
from alm_vcard.models import Category, Email, Adr, Tel, Url

class AppStateViewSet(viewsets.ViewSet):

    @list_route(methods=['get'], url_path='crm')
    def crm(self, request, format=None):
        objects = {
            'categories': self.get_categories(),
            'constants': self.get_constants(),
            'hashtags': self.get_hashtags(),
        }
        return Response(objects)

    @list_route(methods=['get'], url_path='crm/categories')
    def categories(self, request, format=None):
        objects = {
            'objects': self.get_categories()
        }
        return Response(objects)

    @list_route(methods=['get'], url_path='crm/hashtags')
    def hashtags(self, request, format=None):
        objects = {
            'objects': self.get_hashtags()
        }
        return Response(objects)

    @list_route(methods=['get'], url_path='crm/counters')
    def counters(self, request, format=None):
        objects = {
            'shares': self.get_new_shares(),
            'activities': self.get_new_activities(),
        }
        return Response(objects)

    @list_route(methods=['get'], url_path='dashboard')
    def dashboard(self, request, format=None):
        objects = {
            'objects': get_dashboard(request.company.id, request.user.id)
        }
        return Response(objects)

    @list_route(methods=['get'], url_path='active_deals')
    def active_deals(self, request, format=None):
        objects = get_active_deals(request.company.id, request.user.id)
        return Response(objects)

    @list_route(methods=['get'], url_path='active_contacts')
    def active_contacts(self, request, format=None):
        objects = get_active_contacts(request.company.id, request.user.id)
        return Response(objects)

    def get_categories(self):
        return [x.data for x in Category.objects.filter(
            vcard__contact__company_id=self.request.company.id)
        ]

    def get_constants(self):
        return {
            'sales_cycle': {
                'statuses': SalesCycle.STATUSES_OPTIONS,
                'statuses_hash': SalesCycle.STATUSES_DICT
            },
            'sales_cycle_log_entry': {
                'types_hash': SalesCycleLogEntry.TYPES_DICT
            },
            'contact': {
                'tp': Contact.TYPES_OPTIONS,
                'tp_hash': Contact.TYPES_DICT
            },
            'vcard': {
                'email': {'types': Email.TYPE_CHOICES},
                'adr': {'types': Adr.TYPE_CHOICES},
                'tel': {'types': Tel.TYPE_CHOICES},
                'url': {'types': Url.TYPE_CHOICES}
            }
        }

    def get_hashtags(self):
        return [{
                    'id': x.id, 
                    'text': x.text, 
                    'count': x.references.count()
                } for x in HashTag.objects.filter(company_id=self.request.company.id)
        ]

    def get_new_shares(self):
        return Share.objects.filter(company_id=self.request.company.id, share_to=self.request.user, is_read=False).count()

    def get_new_activities(self):
        feed = Activity.objects.filter(company_id=self.request.company.id)
        return ActivityRecipient.objects.filter(activity_id__in=feed.values_list('id', flat=True),  \
                                                 user_id=self.request.user.id, \
                                                 has_read=False) \
                                         .count()

