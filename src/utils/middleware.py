import tldextract


class GetSubdomainMiddleware(object):

    def process_request(self, request):
        request.subdomain = tldextract.extract(
            request.META['HTTP_HOST']).subdomain
