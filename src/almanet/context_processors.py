from django.conf import settings
from alm_vcard.forms import VCardUploadForm

def available_subdomains(request):
    sds = dict(**settings.SUBDOMAIN_MAP)
    sds['BUSY_SUBDOMAINS'] = settings.BUSY_SUBDOMAINS
    return sds

def misc(request):
    return {
        'DEFAULT_SERVICE': settings.DEFAULT_SERVICE
    }

def get_vcard_upload_form(request):
    return {'vcard_upload_form':VCardUploadForm}