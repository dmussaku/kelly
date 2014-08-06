from django import template

from utils import reverse

register = template.Library()

@register.simple_tag
def subdomain_url(view, subdomain='', *args, **kwargs):
    if subdomain is '':
        subdomain = None

    return reverse(view, subdomain=subdomain, args=args, kwargs=kwargs)
