from alm_crm.models import Contact, SalesCycle, Activity
from alm_vcard.models import VCard
import json

def prepopulate_cache():
	Contact.cache_all()
	print '{} Contacts have been cached'.format(Contact.objects.count())
	VCard.cache_all()
	print '{} VCards have been cached'.format(VCard.objects.count())
	SalesCycle.cache_all()
	print '{} SalesCycles have been cached'.format(SalesCycle.objects.count())
	# Activity.cache_all()
	# print '{} Activities have been cached'.format(Activity.objects.count())


def pre():
	prepopulate_cache()