 # Import template library
from almanet.url_resolvers import reverse
from django import template
import urlparse
from django.utils.safestring import mark_safe
from django.template.defaulttags import URLNode, url
from django.core.serializers.json import DjangoJSONEncoder
import json as json_ser

register = template.Library()


@register.filter
def json(obj):
    if isinstance(obj, str):
        return obj
    serialized = json_ser.dumps(
        obj, ensure_ascii=True, separators=(',', ':'),
        cls=DjangoJSONEncoder)
    return mark_safe(serialized)


# Register filter

@register.filter
def durated(value, arg=''):

    """
    #######################################################
    #                                                     #
    #   Seconds-to-Duration Template Tag                  #
    #   Dan Ward 2009 (http://d-w.me)                     #
    #                                                     #
    #######################################################

    Usage: {{ VALUE|durated[:"long"] }}

    NOTE: Please read up 'Custom template tags and filters'
          if you are unsure as to how the template tag is
          implemented in your project.
    """

    # Place seconds in to integer
    secs = int(value)

    # If seconds are greater than 0
    if secs > 0:

        # Import math library
        import math

        # Place durations of given units in to variables
        daySecs = 86400
        hourSecs = 3600
        minSecs = 60

        # If short string is enabled
        if arg != 'long':

            # Set short names
            dayUnitName = ' day'
            hourUnitName = ' hr'
            minUnitName = ' min'
            secUnitName = ' sec'

            # Set short duration unit splitters
            lastDurSplitter = ' '
            nextDurSplitter = lastDurSplitter

        # If short string is not provided or any other value
        else:

            # Set long names
            dayUnitName = ' day'
            hourUnitName = ' hour'
            minUnitName = ' minute'
            secUnitName = ' second'

            # Set long duration unit splitters
            lastDurSplitter = ' and '
            nextDurSplitter = ', '

        # Create string to hold outout
        durationString = ''

        # Calculate number of days from seconds
        days = int(math.floor(secs / int(daySecs)))

        # Subtract days from seconds
        secs = secs - (days * int(daySecs))

        # Calculate number of hours from seconds (minus number of days)
        hours = int(math.floor(secs / int(hourSecs)))

        # Subtract hours from seconds
        secs = secs - (hours * int(hourSecs))

        # Calculate number of minutes from seconds (minus number of days and hours)
        minutes = int(math.floor(secs / int(minSecs)))

        # Subtract days from seconds
        secs = secs - (minutes * int(minSecs))

        # Calculate number of seconds (minus days, hours and minutes)
        seconds = secs

        # If number of days is greater than 0
        if days > 0:

            # Add multiple days to duration string
            durationString += ' ' + str(days) + dayUnitName + (days > 1 and 's' or '')

        # Determine if next string is to be shown
        if hours > 0:

            # If there are no more units after this
            if minutes <= 0 and seconds <= 0:

                # Set hour splitter to last
                hourSplitter = lastDurSplitter

            # If there are unit after this
            else:

                # Set hour splitter to next
                hourSplitter = (len(durationString) > 0 and nextDurSplitter or '')

        # If number of hours is greater than 0
        if hours > 0:

            # Add multiple days to duration string
            durationString += hourSplitter + ' ' + str(hours) + hourUnitName + (hours > 1 and 's' or '')

        # Determine if next string is to be shown
        if minutes > 0:

            # If there are no more units after this
            if seconds <= 0:

                # Set minute splitter to last
                minSplitter = lastDurSplitter

            # If there are unit after this
            else:

                # Set minute splitter to next
                minSplitter = (len(durationString) > 0 and nextDurSplitter or '')

        # If number of minutes is greater than 0
        if minutes > 0:

            # Add multiple days to duration string
            durationString += minSplitter + ' ' + str(minutes) + minUnitName + (minutes > 1 and 's' or '')

        # Determine if next string is last
        if seconds > 0:

            # Set second splitter
            secSplitter = (len(durationString) > 0 and lastDurSplitter or '')

        # If number of seconds is greater than 0
        # if seconds > 0:

        #     # Add multiple days to duration string
        #     durationString += secSplitter + ' ' + str(seconds) + secUnitName + (seconds > 1 and 's' or '')

        # Return duration string
        return durationString.strip()

    # If seconds are not greater than 0
    else:

        # Provide 'No duration' message
        return '0 mins'


@register.filter('field_type')
def klass(ob):
    return ob.__class__.__name__


@register.filter(name='widget_original_type')
def widet_original_type(field):
    from django.forms.widgets import Widget

    def go_deep(widget):
        if widget.__mro__[1] == Widget:
            return widget.__name__.lower()
        else:
            idx = -1
            for i, mro_type in enumerate(widget.__mro__):
                if mro_type == Widget:
                    idx = i - 1
                    break
            if idx == -1:
                raise Exception(
                    "Could not found type of widget in widget_original_type")
            return widget.__mro__[idx].__name__.lower()

    if hasattr(field, 'field') and \
            hasattr(field.field, 'widget') and field.field.widget:

        return go_deep(field.field.widget.__class__)


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def div(value, arg):
    return value * 1. / float(arg)


@register.filter
def diff(lval, rval):
    return abs(lval - rval)


@register.filter
def key(d, key_name):
    try:
        return d[key_name]
    except KeyError:
        return d[int(key_name)]


@register.filter
def georev(d, where):
    return d[(where.x, where.y)]


@register.filter
def index_of(d, key_name):
    return d[int(key_name)]


@register.filter
def joinby(value, arg):
    return arg.join(map(str, value))


class AbsoluteURLNode(URLNode):
    def render(self, context):
        path = super(AbsoluteURLNode, self).render(context)
        try:
            return urlparse.urljoin(context['DOMAIN_PREFIX'], path)
        except KeyError:
            from django.conf import settings
            return urlparse.urljoin(settings.SITE_DOMAIN, path)


def absurl(parser, token, node_cls=AbsoluteURLNode):
    """Just like {% url %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return node_cls(
        view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)
absurl = register.tag(absurl)


@register.simple_tag
def subdomain_url(view, subdomain='', *args, **kwargs):
    """Like url but accepts subdomain parameter"""
    if subdomain is '':
        subdomain = None
    return reverse(view, subdomain=subdomain, args=args, kwargs=kwargs)

@register.inclusion_tag('almanet/tags/con_discon_button.html')
def connect_disconnect_button(user, product):
    """ Show connect or disconnect links according to user - product relation """
    return {
        'user': user,
        'product': product,
        'connected': user.is_product_connected(product)
    }
