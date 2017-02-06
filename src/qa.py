#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "almanet.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", 'QAConfiguration')

    from configurations.management import execute_from_command_line
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            os.environ['DJANGO_CONFIGURATION'] = 'TestConfiguration'
    
    from django.core import urlresolvers
    from almanet.url_resolvers import reverse, reverse_lazy
    urlresolvers.reverse = reverse
    urlresolvers.reverse_lazy = reverse_lazy
    execute_from_command_line(sys.argv)
    