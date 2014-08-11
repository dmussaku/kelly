from django.conf import settings

def available_subdomains(request):

	return {'available_subdomains': settings.SUBDOMAINS}