"""
WSGI config for src project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "almanet.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'DemoConfiguration')


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from configurations import importer
importer.install()

from . import celery

for i in xrange(5):
	print "PLEASE DONT FORGET PRECACHE"


# # todo! may be in future it s better to make an async task.
# preparations.pre()
#celery.prepare_cache.delay()