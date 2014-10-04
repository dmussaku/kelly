from django import template
from django.core.urlresolvers import reverse
register = template.Library()


@register.inclusion_tag('crm/contacts/_contact.html')
def show_contact(contact):
    return {'contact': contact}


@register.inclusion_tag('crm/_activity.html')
def show_activity(activity):
    return {'activity': activity}


@register.simple_tag
def crm_url(view, url='', *args, **kwargs):
    """Like url but add 'crm' parameter to works"""
    if url is '':
        url = None
    kwargs.update({'slug': 'crm'})
    return reverse(view, args=args, kwargs=kwargs)
