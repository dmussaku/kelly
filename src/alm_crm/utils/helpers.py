from django.db.models import Q

from alm_crm.models import SalesCycle, Contact, Activity
from alm_crm.serializers import ContactSerializer, SalesCycleSerializer

def get_dashboard(company_id, user_id):
    return {
        'panels': {
            'sales_cycles': SalesCycle.get_panel_info(company_id=company_id, user_id=user_id),
            'contacts': Contact.get_panel_info(company_id=company_id, user_id=user_id),
            'activities': Activity.get_panel_info(company_id=company_id, user_id=user_id),
        },
        

        # 'active_contacts': { 
        #     'all': {
        #         'days': map(lambda x: ContactSerializer(x, parent=True).data,
        #                     active_contacts['all']['days']
        #                 ),
        #         'weeks': map(lambda x: ContactSerializer(x, parent=True).data,
        #                     active_contacts['all']['weeks']
        #                 ),
        #         'months': map(lambda x: ContactSerializer(x, parent=True).data,
        #                     active_contacts['all']['months']
        #                 ),
        #     },
        #     'my': {
        #         'days': map(lambda x: ContactSerializer(x, parent=True).data,
        #                     active_contacts['my']['days']
        #                 ),
        #         'weeks': map(lambda x: ContactSerializer(x, parent=True).data,
        #                     active_contacts['my']['weeks']
        #                 ),
        #         'months': map(lambda x: ContactSerializer(x, parent=True).data,
        #                     active_contacts['my']['months']
        #                 ),
        #     },
        # }
    }

    return rv

def get_active_deals(company_id, user_id):
    active_deals = SalesCycle.get_active_deals(company_id=company_id, user_id=user_id)
    return { 
        'all': {
            'days': SalesCycleSerializer(active_deals['all']['days'], many=True, contact=True).data,
            'weeks': SalesCycleSerializer(active_deals['all']['weeks'], many=True, contact=True).data,
            'months': SalesCycleSerializer(active_deals['all']['months'], many=True, contact=True).data,
        },
        'my': {
            'days': SalesCycleSerializer(active_deals['my']['days'], many=True, contact=True).data,
            'weeks': SalesCycleSerializer(active_deals['my']['weeks'], many=True, contact=True).data,
            'months': SalesCycleSerializer(active_deals['my']['months'], many=True, contact=True).data,
        },
    }

def get_active_contacts(company_id, user_id):
    active_contacts = Contact.get_active_contacts(company_id=company_id, user_id=user_id)
    return { 
            'all': {
                'days': ContactSerializer(active_contacts['all']['days'], many=True).data,
                'weeks': ContactSerializer(active_contacts['all']['weeks'], many=True).data,
                'months': ContactSerializer(active_contacts['all']['months'], many=True).data,
            },
            'my': {
                'days': ContactSerializer(active_contacts['my']['days'], many=True).data,
                'weeks': ContactSerializer(active_contacts['my']['weeks'], many=True).data,
                'months': ContactSerializer(active_contacts['my']['months'], many=True).data,
            },
        }