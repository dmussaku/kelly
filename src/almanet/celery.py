from __future__ import absolute_import
# set the default Django settings module for the 'celery' program.
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almanet.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'BaseConfiguration')


from celery import Celery
from django.conf import settings

from configurations import importer
importer.install()
# configurations.setup()

# app = Celery('almanet')
app = Celery('almanet',
     broker='amqp://guest@localhost//',
     backend='djcelery.backends.database:DatabaseBackend',
     include=['alm_crm.tasks'] #References your tasks. Donc forget to put the whole absolute path.
     )

# app.conf.update(
#     CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
# )

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))