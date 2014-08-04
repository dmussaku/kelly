"""
Django settings for src project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def rel(*x):
    return os.path.join(BASE_DIR, *x)

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
    'south',
    'almanet',   # commons, entry point
    'alm_user',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'almanet.urls'

WSGI_APPLICATION = 'almanet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel('../..', 'db.sqlite3'),
    }
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
SERVER_EMAIL = u'Alma.net services <r.kamun@gmail.com>'
DEFAULT_FROM_EMAIL = u'Alma.net services <r.kamun@gmail.com>'

EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'
MANDRILL_API_KEY = 'pMC2w0tuVIuYRZiAjbu8mA'
ADMINS = (('Rustem', 'adm+r.kamun@v3na.com'),)
MANAGERS = ADMINS
BCC_EMAILS = ()


from django.core.urlresolvers import reverse_lazy

LOGIN_REDIRECT_URL = reverse_lazy('user_list')

AUTH_USER_MODEL = 'alm_user.User'
ANONYMOUS_USER_ID = -1
ANONYMOUS_DEFAULT_USERNAME_VALUE = 'Anonymous'
PASSWORD_RESET_TIMEOUT_DAYS = 15

DB_PREFIX = 'alma_{}'

AUTHENTICATION_BACKENDS = (
    'alm_user.authbackend.MyAuthBackend',)


COUNTRIES = [('Kazakhstan', 'Kazakhstan'), ('Russia', 'Russia')]

SITE_NAME = 'Alma.net'
SITE_DOMAIN = 'http://localhost:8000'
