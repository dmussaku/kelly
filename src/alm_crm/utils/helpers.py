from django.db.models import Q

from alm_crm.models import SalesCycle, Contact, Activity
from alm_crm.serializers import ContactSerializer, SalesCycleSerializer

def get_dashboard(company_id, user_id):
    active_deals = SalesCycle.get_active_deals(company_id=company_id, user_id=user_id)
    # active_contacts = Contact.get_active_contacts(company_id=company_id, user_id=user_id)

    rv = {
        'panels': {
            'sales_cycles': SalesCycle.get_panel_info(company_id=company_id, user_id=user_id),
            'contacts': Contact.get_panel_info(company_id=company_id, user_id=user_id),
            'activities': Activity.get_panel_info(company_id=company_id, user_id=user_id),
        },
        # 'active_deals': { 
        #     'all': {
        #         'days': map(lambda x: SalesCycleSerializer(x, contact=True).data,
        #                     active_deals['all']['days']
        #                 ),
        #         'weeks': map(lambda x: SalesCycleSerializer(x, contact=True).data,
        #                     active_deals['all']['weeks']
        #                 ),
        #         'months': map(lambda x: SalesCycleSerializer(x, contact=True).data,
        #                     active_deals['all']['months']
        #                 ),
        #     },
        #     'my': {
        #         'days': map(lambda x: SalesCycleSerializer(x, contact=True).data,
        #                     active_deals['my']['days']
        #                 ),
        #         'weeks': map(lambda x: SalesCycleSerializer(x, contact=True).data,
        #                     active_deals['my']['weeks']
        #                 ),
        #         'months': map(lambda x: SalesCycleSerializer(x, contact=True).data,
        #                     active_deals['my']['months']
        #                 ),
        #     },
        # },
        # 'active_deals': { 
        #     'all': {
        #         'days': SalesCycleSerializer(active_deals['all']['days'], many=True, contact=True).data,
        #         'weeks': SalesCycleSerializer(active_deals['all']['weeks'], many=True, contact=True).data,
        #         'months': SalesCycleSerializer(active_deals['all']['months'], many=True, contact=True).data,
        #     },
        #     'my': {
        #         'days': SalesCycleSerializer(active_deals['my']['days'], many=True, contact=True).data,
        #         'weeks': SalesCycleSerializer(active_deals['my']['weeks'], many=True, contact=True).data,
        #         'months': SalesCycleSerializer(active_deals['my']['months'], many=True, contact=True).data,
        #     },
        # },

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