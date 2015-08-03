from alm_crm.models import Contact, SalesCycle
from alm_vcard.models import VCard
import json

def prepopulate_cache():
	Contact.cache_all()
	print 'Contacts have been cached'
	VCard.cache_all()
	print 'VCards have been cached'
	SalesCycle.cache_all()
	print 'SalesCycles have been cached'


def pre():
	prepopulate_cache()