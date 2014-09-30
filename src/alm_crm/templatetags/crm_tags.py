from django import template
register = template.Library()


@register.inclusion_tag('crm/contacts/_contact.html')
def show_contact(contact):
    return {'contact': contact}


@register.inclusion_tag('crm/_activity.html')
def show_activity(activity):
    return {'activity': activity}
