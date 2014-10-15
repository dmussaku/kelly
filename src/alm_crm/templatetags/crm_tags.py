from django import template
from django.core.urlresolvers import reverse
register = template.Library()


@register.inclusion_tag('crm/contacts/_contact.html')
def show_contact(contact):
    return {'contact': contact}


@register.inclusion_tag('crm/activity.html')
def show_activity(activity, **kwargs):
    kwargs.update({'activity': activity})
    print kwargs
    return kwargs


@register.simple_tag
def crm_url(view, url='', *args, **kwargs):
    """Like url but add service_slug = 'crm' kwarg,
    to work with urls in crm/app_urls.py"""
    if url is '':
        url = None
    kwargs.update({'service_slug': 'crm'})
    return reverse(view, args=args, kwargs=kwargs)
