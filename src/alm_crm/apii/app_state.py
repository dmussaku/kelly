from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from alm_crm.utils.helpers import get_dashboard
from alm_crm.serializers import MilestoneSerializer
from alm_crm.models import Contact, SalesCycleLogEntry, HashTag, SalesCycle, SalesCycleLogEntry, Share, Activity
from alm_vcard.models import Category, Email, Adr, Tel, Url

class AppStateView(viewsets.ViewSet):

    @list_route(methods=['get'], url_path='crm')
    def crm(self, request, format=None):
        objects = {
            'categories': self.get_categories(),
            'constants': self.get_constants(),
            'hashtags': self.get_hashtags(),
            'badges': {
                'shares': self.get_new_shares(),
                'activities': self.get_new_activities(),
            }
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

    @list_route(methods=['get'], url_path='dashboard')
    def dashboard(self, request, format=None):
        objects = {
            'objects': get_dashboard(request.company.id, request.user.id)
        }
        return Response(objects)

    def get_categories(self):
        return [x.data for x in Category.objects.filter(
            vcard__contact__company_id=self.request.company.id)
        ]

    def get_constants(self):
        return {
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
        return len([
            act for act in Activity.objects.filter(company_id=self.request.company.id) if not act.has_read(self.request.user.id)
        ])

