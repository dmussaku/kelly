#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django settings for src project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import
import os
import imp
from django.utils.functional import lazy
from configurations import Configuration, pristinemethod
from configurations.utils import uppercase_attributes
from django.utils.translation import ugettext_lazy as _
from celery.schedules import crontab
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def rel(*x):
    return os.path.join(BASE_DIR, *x)


class SubdomainConfiguration:
    MY_SD = 'my'
    BILLING_SD = 'billing'
    API_SD = 'api'
    WWW_SD = 'www'
    MARKETPLACE_SD = 'marketplace'
    SHOP_SD = 'shop'
    BUSY_SUBDOMAINS = (MY_SD,
                       BILLING_SD,
                       API_SD,
                       WWW_SD,
                       MARKETPLACE_SD,
                       SHOP_SD,)

    @property
    def SUBDOMAIN_MAP(self):
        if not hasattr(self, '__SUBDOMAIN_MAP'):
            rv = {}
            for attr in dir(self.__class__):
                if attr.endswith('SD'):
                    rv[attr] = getattr(self.__class__, attr)
            setattr(self, '__SUBDOMAIN_MAP', rv)
        return getattr(self, '__SUBDOMAIN_MAP')

    @property
    def CORS_ORIGIN_WHITELIST(self):

        def __inner():
            from alm_company.models import Company
            subd = ["%s.%s" % (c.subdomain, self.SITE_NAME)
                    for c in Company.objects.all()]
            return (self.SITE_NAME, ) + tuple(subd)
        return lazy(__inner, tuple)


def FileSettings(path):
    path = os.path.expanduser(path)

    class Holder(object):

        def __init__(self, *args, **kwargs):
            mod = imp.new_module('almanet.local')
            mod.__file__ = path

            try:
                execfile(path, mod.__dict__)
            except IOError, e:
                print("Notice: Unable to load configuration file %s (%s), "
                      "using default settings\n\n" % (path, e.strerror))

            for name, value in uppercase_attributes(mod).items():
                if hasattr(self, name):
                    original_value = getattr(self, name)
                    if isinstance(original_value, (tuple, list)):
                        if value.startswith('+'):
                            value = tuple(original_value) + tuple(value[1:].split(','))
                        else:
                            value = tuple([value])
                setattr(self, name, value)

    return Holder


class BaseConfiguration(SubdomainConfiguration, Configuration):

    # Celery settings

    BROKER_URL = 'amqp://guest:guest@localhost//'
    
    #: Only add pickle to this list if your broker is secured
    #: from unwanted access (see userguide/security.html)
    CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

    CELERYBEAT_SCHEDULE = {
        'cleanup-inactive-files': {
            'task': 'alm_crm.tasks.cleanup_inactive_files',
            'schedule': crontab(minute=0, hour=0) # execute every midnight
        },
    }


    @pristinemethod
    def reverse_lazy(viewname, **kw):
        def __inner():
            from almanet.url_resolvers import reverse
            return reverse(viewname, **kw)

        return lazy(__inner, str)

    TEST_RUNNER = "djnose2.TestRunner"

    BASE_DIR = BASE_DIR
    TEMP_DIR = rel(BASE_DIR, 'temp_dir')

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'ky(-3$vh&n^kmg#ft2)k3e^61=yz)%!@m#k&)jmx1%c200*1o#'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    TEMPLATE_DEBUG = True

    ALLOWED_HOSTS = ['*']

    # Application definition
    INSTALLED_APPS = (
        'django.contrib.admin',
        # 'django.contrib.auth',
        'mailviews',
        'djrill',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        # 'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_hosts',
        'south',
        'timezone_field',
        'almanet',   # commons, entry point
        'alm_user',
        'alm_company',
        'alm_vcard',
        'alm_crm',
        'corsheaders',
        'tastypie',
        'tastypie_swagger',
        'django_extensions',
        'almastorage',
        'djcelery',
        'kkb',
    )

    MIDDLEWARE_CLASSES = (
        'almanet.middleware.GetSubdomainMiddleware',
        'django.middleware.common.CommonMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django_hosts.middleware.HostsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.middleware.gzip.GZipMiddleware',
        'almanet.middleware.ForceDefaultLanguageMiddleware',
        # 'almanet.middleware.AlmanetSessionMiddleware',
        # 'almanet.middleware.MyAuthenticationMiddleware',
    )

    SESSION_COOKIE_DOMAIN = '.alma.net'

    ROOT_URLCONF = 'almanet.urls'

    ROOT_HOSTCONF = 'almanet.hosts'
    PARENT_HOST = 'alma.net:8000'
    DEFAULT_HOST = 'default'

    HOSTCONF_REGEX = r'alma\.net:8000'

    WSGI_APPLICATION = 'almanet.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/1.6/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('../..', 'db.sqlite3'),
        },
        'test': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('../..', 'test_db.sqlite3'),
        },
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211'
        }
    }

    # Internationalization
    # https://docs.djangoproject.com/en/1.6/topics/i18n/

    LANGUAGE_CODE = 'ru'

    LANGUAGES = (
        ('ru', _('Russian')),
        ('en', _('English')),
    )

    TIME_ZONE = 'Asia/Almaty'

    DATETIME_FORMAT = 'H:i, d N y'
    DATETIME_FORMAT_NORMAL = '%H:%M, %d %b %y'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

    TASTYPIE_DEFAULT_FORMATS = ['json']

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.core.context_processors.request',
        'django.contrib.messages.context_processors.messages',
        "django.contrib.auth.context_processors.auth",
        'almanet.context_processors.available_subdomains',
        'almanet.context_processors.misc',
        # 'almanet.context_processors.get_vcard_upload_form',
        # 'launch.context_processors.launch',
    )

    TEMPLATE_DIRS = (
        rel('templates'),
    )

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.6/howto/static-files/

    MEDIA_ROOT = rel('../..', 'media')
    MEDIA_URL = '/media/'

    STATIC_URL = '/static/'
    STATIC_ROOT = rel('../..', 'static')
    STATICFILES_DIRS = (
        rel('static'),
    )
    LOCALE_PATHS = (
        rel('locale'),
    )
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

    TASTYPIE_SWAGGER_API_MODULE = 'almanet.urls.v1_api'

    EMAIL_HOST_USER = 'adm@v3na.com'
    EMAIL_HOST_PASSWORD = ''
    EMAIL_SUBJECT_PREFIX = '[alma.net] '
    SERVER_EMAIL = u'Almasales <r.kamun@gmail.com>'
    DEFAULT_FROM_EMAIL = u'Almasales <r.kamun@gmail.com>'
    SUPPORT_EMAIL = 'support@v3na.com'
    EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'
    MANDRILL_API_KEY = 'RcETDKfvxER6iYnJ70DuyA'
    ADMINS = (('Rustem', 'r.kamun@gmail.com'),
              ('Askhat', 'askhat.omarov91@gmail.com'),
              ('Sattar', 'sattar.stamkul@gmail.com'),
              ('Danik', 'dmussaku@gmail.com'),)
    MANAGERS = ADMINS
    BCC_EMAILS = ()

    @property
    def LOGIN_REDIRECT_URL(self):
        return self.__class__.reverse_lazy('user_profile_url',
                                           subdomain=self.MY_SD)
    @property
    def LOGIN_URL(self):
        return self.__class__.reverse_lazy('user_login', subdomain=None)

    @property
    def LOGOUT_URL(self):
        return self.__class__.reverse_lazy('user_logout', subdomain=None)

    AUTH_USER_MODEL = 'alm_user.User'
    ANONYMOUS_USER_ID = -1
    ANONYMOUS_DEFAULT_USERNAME_VALUE = 'Anonymous'
    PASSWORD_RESET_TIMEOUT_DAYS = 15

    DB_PREFIX = 'alma_{}'
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',)  # for admin

    # AUTHENTICATION_BACKENDS = (
    #     'alm_user.auth_backend.MyAuthBackend',)


    SITE_NAME = 'alma.net'
    SITE_DOMAIN = 'http://alma.net:8000'

    DEFAULT_URL_SCHEME = 'http'

    DEFAULT_SERVICE = 'crm'

    TASTYPIE_DEFAULT_FORMATS = ['json']

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }

    USE_PROFILER = False   # degbug toolbar on/off

    GCALSYNC_APIKEY = 'AIzaSyAlLnRj_quAiDlXs3G07Xn1yGL2L_dJwuI'
    GCALSYNC_CREDENTIALS = rel('google_api_cred.json')

    SW_USERNAME = 'ALMASALES'
    SW_KEY = 'x3IFqvHB'
    SW_AUTH_URL = 'http://178.88.64.78/auth/v1.0'

    MERCHANT_CERTIFICATE_ID = "" # Серийный номер сертификата Cert Serial Number
    MERCHANT_NAME = "" # Название магазина (продавца) Shop/merchant Name
    PRIVATE_KEY_FN = "" # Абсолютный путь к закрытому ключу Private cert path
    PRIVATE_KEY_PASS = "" # Пароль к закрытому ключу Private cert password
    PUBLIC_KEY_FN = "" # Абсолютный путь к открытому ключу Public cert path
    MERCHANT_ID="" # Терминал ИД в банковской Системе

    
    RUSTEM_SETTINGS = False


class DevConfiguration(
        FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    # CORS_ORIGIN_WHITELIST = (
    #     'alma.net:8000',
    #     'almacloud.alma.net:8000'
    # )
    SITE_NAME = 'alma.net:8000'
    CSRF_COOKIE_DOMAIN = '.alma.net'
    CORS_ALLOW_CREDENTIALS = True
    BROKER_URL = 'amqp://dev:dev@almasales.kz:5672//almasales/dev'

    RUSTEM_SETTINGS = False


class QAConfiguration(DevConfiguration):
    USE_PROFILER = True
    # DEBUG_TOOLBAR_PATCH_SETTINGS = False

    @classmethod
    def pre_setup(cls):
        cls.INSTALLED_APPS += ('debug_toolbar', 'debug_panel',)
        cls.MIDDLEWARE_CLASSES += (
            'debug_panel.middleware.DebugPanelMiddleware',)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('../..', 'qadb.sqlite3'),
        },
        'test': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('../..', 'test_qadb.sqlite3'),
        },
    }


class TestConfiguration(
        FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
    SELENIUM_TESTSERVER_HOST = 'http://10.8.0.18'

    #PARENT_HOST = 'alma.net:8000'
    #SITE_DOMAIN = PARENT_HOST
    SELENIUM_TESTSERVER_PORT = '4444'
    SELENIUM_CAPABILITY = 'FIREFOX'
    DEFAULT_SERVER_PORT = 8000
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('../..', 'test_db.sqlite3'),
        },
        # 'test': {
        #     'ENGINE': 'django.db.backends.sqlite3',
        #     'NAME': rel('../..', 'test_db.sqlite3'),
        # },
    }
    DEBUG = True


class StagingConfiguration(FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
    DEBUG = False
    PARENT_HOST = 'origamibar.kz:3082'
    HOSTCONF_REGEX = r'origamibar\.kz:3082'

    SITE_NAME = 'origamibar.kz:3082'
    SITE_DOMAIN = 'http://origamibar.kz:3082'
    CSRF_COOKIE_DOMAIN = '.origamibar.kz'
    SESSION_COOKIE_DOMAIN = '.origamibar.kz'
    # CORS_ORIGIN_WHITELIST = (
    #     'almasales.kz',
    #     'almacloud.almasales.kz',
    #     'arta.almasales.kz'
    # )
    CORS_ALLOW_CREDENTIALS = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'qa_almanet',
            'TEST_NAME': 'test_almanet',
            'USER': 'xepa4ep',
            'PASSWORD': 'f1b0nacc1',
            'HOST': 'db.alma.net',
            'PORT': '5432'
        }
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211'
        }
    }

    MEDIA_ROOT = os.path.expanduser('~/.almanet/stagemedia/')
    STATIC_ROOT = os.path.expanduser('~/.almanet/stagestatic/')
    BROKER_URL = 'amqp://stage:n0easyway1n@10.10.10.245:5672//almasales/stage'
    CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'


class StagingConfiguration2(FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
    DEBUG = False
    PARENT_HOST = 'almasales.qa2:4369'
    HOSTCONF_REGEX = r'almasales\.qa2:4369'

    SITE_NAME = 'almasales.qa2:4369'
    SITE_DOMAIN = 'http://almasales.qa2:4369'
    CSRF_COOKIE_DOMAIN = '.almasales.qa2'
    SESSION_COOKIE_DOMAIN = '.almasales.qa2'
    # CORS_ORIGIN_WHITELIST = (
    #     'almasales.kz',
    #     'almacloud.almasales.kz',
    #     'arta.almasales.kz'
    # )
    CORS_ALLOW_CREDENTIALS = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'qa2_almanet',
            'TEST_NAME': 'test_almanet',
            'USER': 'xepa4ep',
            'PASSWORD': 'f1b0nacc1',
            'HOST': 'db.alma.net',
            'PORT': '5432'
        }
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211'
        }
    }

    MEDIA_ROOT = os.path.expanduser('~/.almanet/stagemedia/')
    STATIC_ROOT = os.path.expanduser('~/.almanet/stagestatic/')
    BROKER_URL = 'amqp://stage:n0easyway1n@10.10.10.245:5672//almasales/stage'
    CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'



class DemoConfiguration(FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
    DEBUG = False
    PARENT_HOST = 'almasales.kz'
    HOSTCONF_REGEX = r'almasales\.kz'

    SITE_NAME = 'almasales.kz'
    SITE_DOMAIN = 'http://almasales.kz'
    CSRF_COOKIE_DOMAIN = '.almasales.kz'
    SESSION_COOKIE_DOMAIN = '.almasales.kz'
    # CORS_ORIGIN_WHITELIST = (
    #     'almasales.kz',
    #     'almacloud.almasales.kz',
    #     'arta.almasales.kz'
    # )
    CORS_ALLOW_CREDENTIALS = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'almanet',
            'TEST_NAME': 'test_almanet',
            'USER': 'xepa4ep',
            'PASSWORD': 'f1b0nacc1',
            'HOST': 'db.alma.net',
            'PORT': '5432'
        }
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': 'db.alma.net:11211'
        }
    }

    MEDIA_ROOT = os.path.expanduser('~/.almanet/media/')
    STATIC_ROOT = os.path.expanduser('~/.almanet/static/')
