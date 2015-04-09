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

	activities = map(lambda sc: sc.find_latest_activity(), sales_cycles)
	rv['undefined'] = len(filter(lambda a: a == None or a.milestone == None, activities))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	act_in_funnel = [a for a in activities if a != None and a.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len(act_in_funnel)
		act_in_funnel = [a for a in act_in_funnel if a.milestone.id != m.id]
	return rv

def build_realtime_funnel(subscription_id):
	rv = {
		'report_name': 'realtime_funnel'
	}
	sales_cycles = SalesCycle.objects.filter(subscription_id=subscription_id, is_global=False)
	rv['total'] = len(sales_cycles)

	activities = map(lambda sc: sc.find_latest_activity(), sales_cycles)
	rv['undefined'] = len(filter(lambda a: a == None or a.milestone == None, activities))
	
	rv['funnel'] = {}
	milestones = Milestone.objects.filter(subscription_id=subscription_id)
	act_in_funnel = [a for a in activities if a != None and a.milestone != None]
	for m in milestones:
		rv['funnel'][m.id] = len([a for a in act_in_funnel if a.milestone.id == m.id])
	return rv
		