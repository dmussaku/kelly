from __future__ import absolute_import
# set the default Django settings module for the 'celery' program.
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almanet.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'DevConfiguration')


from celery import Celery
from django.conf import settings

from configurations import importer
importer.install()

app = Celery('almanet')

# override application level settings
app.config_from_object(settings)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

from . import preparations

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def prepare_cache(self):
	preparations.pre()
	pass