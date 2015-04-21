import re
from alm_crm.models import (
	SalesCycle,
	Milestone
	)

def build_funnel(subscription_id):
	rv = {
		'report_name': 'funnel'
	}
	sales_cycles = SalesCycle.objects.filter(subscription_id=subscription_id, is_global=False)
	rv['total'] = len(sales_cycles)

	rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	
	sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len(sc_in_funnel)
		sc_in_funnel = [sc for sc in sc_in_funnel if sc.milestone.id != m.id]
	return rv

def build_realtime_funnel(subscription_id):
	rv = {
		'report_name': 'realtime_funnel'
	}
	sales_cycles = SalesCycle.objects.filter(subscription_id=subscription_id, is_global=False)
	rv['total'] = len(sales_cycles)

	rv['undefined'] = len(filter(lambda sc: sc.milestone == None, sales_cycles))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	
	sc_in_funnel = [sc for sc in sales_cycles if sc.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len([sc for sc in sc_in_funnel if sc.milestone.id == m.id])
	return rv
		