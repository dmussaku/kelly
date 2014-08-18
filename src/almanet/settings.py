"""
Django settings for src project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import imp
from django.utils.functional import lazy
from configurations import Configuration, pristinemethod
from configurations.utils import uppercase_attributes
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def rel(*x):
    return os.path.join(BASE_DIR, *x)


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
                setattr(self, name, value)

    return Holder

class BaseConfiguration(Configuration):

    @pristinemethod
    def reverse_lazy(viewname, **kw):
        def __inner():
            from utils.url_resolvers import reverse
            return reverse(viewname, **kw)

        return lazy(__inner, str)

    TEST_RUNNER = "djnose2.TestRunner"

    BASE_DIR = BASE_DIR
    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'ky(-3$vh&n^kmg#ft2)k3e^61=yz)%!@m#k&)jmx1%c200*1o#'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    TEMPLATE_DEBUG = True

    ALLOWED_HOSTS = []

    # Application definition
    INSTALLED_APPS = (
        # 'django.contrib.admin',
        # 'django.contrib.auth',
        'mailviews',
        'djrill',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_hosts',
        'south',
        'timezone_field',
        'almanet',   # commons, entry point
        'alm_user',
        'alm_company',
        'utils',
    )

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_hosts.middleware.HostsMiddleware',
        'utils.middleware.GetSubdomainMiddleware',
    )

    SESSION_COOKIE_DOMAIN = '.alma1.net'

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

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.core.context_processors.request',
        'django.contrib.messages.context_processors.messages',
        "django.contrib.auth.context_processors.auth",
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
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

    EMAIL_HOST_USER = 'adm@v3na.com'
    EMAIL_HOST_PASSWORD = ''
    EMAIL_SUBJECT_PREFIX = '[alma.net] '
    SERVER_EMAIL = u'alma1.net services <r.kamun@gmail.com>'
    DEFAULT_FROM_EMAIL = u'alma1.net services <r.kamun@gmail.com>'

    EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'
    MANDRILL_API_KEY = 'pMC2w0tuVIuYRZiAjbu8mA'
    ADMINS = (('Rustem', 'adm+r.kamun@v3na.com'),)
    MANAGERS = ADMINS
    BCC_EMAILS = ()

    @property
    def LOGIN_REDIRECT_URL(self):
        return self.__class__.reverse_lazy('user_profile_url', subdomain='my')

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
        'alm_user.authbackend.MyAuthBackend',)

    SITE_NAME = 'alma.net'
    SITE_DOMAIN = 'http://localhost:8000'

    DEFAULT_URL_SCHEME = 'http'

    COUNTRIES = [('Kazakhstan', 'Kazakhstan'), ('Russia', 'Russia')]
    BUSY_SUBDOMAINS = ['my', 'billing', 'api', 'www', 'marketplace', 'shop']



class DevConfiguration(FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
    #PARENT_HOST = 'alma.net:8000'
    #SITE_DOMAIN = PARENT_HOST
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG


class TestConfiguration(FileSettings('~/.almanet/almanet.conf.py'), BaseConfiguration):
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

