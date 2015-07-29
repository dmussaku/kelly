from alm_crm.models import Contact
from alm_vcard.models import VCard
import json

def prepopulate_cache():
	Contact.cache_all()
	VCard.cache_all()


def pre():
	prepopulate_cache()