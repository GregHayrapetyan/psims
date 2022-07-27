import os
import stripe

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'formtools',
    'psims',
    'phonenumber_field',
]
    

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'psims_web_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'psims.context.context_processor',
                'psims.context.GetNotifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'psims_web_project.wsgi.application'

# if not defined SECRET_KEY in settings_local to use this default value
SECRET_KEY = "m3o05^+!e9&&yf7%+e&h=m0+fx2)v2q21szg^*gu2#amy(8j5zg_w(c@plfj@@)tcc6h(yn_uz@6yd9+5=5b40pe%b)glyse&wot"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEBUG = True


STATIC_URL = '/static/'
LOGIN_REDIRECT_URL = '/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR, ]
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

#set when going to production
#STATIC_ROOT

# REDIS related settings 
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_TRACK_STARTED = True
CELERY_TASK_TRACK_STARTED = True
CELERY_LOG_FILE = os.path.join(

BASE_DIR, 'celery', 'logs')

CELERY_LOG_LEVEL = "INFO"
CELERY_OPTS="--concurrency=1"
CELERY_CONCURENCY = 1
CELERY_NODES=2
STRIPE_SECRET_KEY = 'sk_test_51JJFrhDdwM4weTo42dm2wx8tYnXqyA9oJhVd0fdjtsQ18mBr0TpkwgWgl7ACdYTzBrJKbHuMHIOrljxlmD02H8Eq00KUyQ48qX'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51JJFrhDdwM4weTo4C4ZkDviPNChj4TwwM5aJODHaUAPtn0fn8fRluoGEQPNQPsVckBwxpAVn3bvtxViCBr9qCTpt0090htA3FU'
STRIPE_WEBHOOK_SECRET = 'whsec_kIliqNA3AqP1UVbOz0l6geHLeJORGXHA'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True 
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587  
EMAIL_HOST_USER = 'praedictustest@gmail.com' 
EMAIL_HOST_PASSWORD = 'praedictus123' 
DEFAULT_FROM_EMAIL = 'praedictustest@gmail.com'


# This should always last, to allow local overriding of values
try:
    from .settings_local import *
except ImportError:
    pass

