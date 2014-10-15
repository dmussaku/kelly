from django.conf import settings


def available_subdomains(request):
    sds = dict(**settings.SUBDOMAIN_MAP)
    sds['BUSY_SUBDOMAINS'] = settings.BUSY_SUBDOMAINS
    return sds

def misc(request):
    return {
        'DEFAULT_SERVICE': settings.DEFAULT_SERVICE
    }
