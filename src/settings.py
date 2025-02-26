# src/settings.py
from pathlib import Path
from neo4j import GraphDatabase
from decouple import config
from neomodel import db
from neomodel import config as neo_config
from urllib.parse import urlparse
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5u=1hp5k_(8s^ft&6cumi*b7dyj0x(u^-tppbm#a*hndjw9u1p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [".vercel.app", "127.0.0.1", ".onrender.com", "localhost", "spiritframework.io"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites', # Third party app. Allauth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party auth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Internal apps - Start
    'authentication',
    'chat',
    'journal',
    'patterns',
    'premium',
    # Internal apps - End

    'rest_framework',
    'rest_framework.authtoken',

    'rest_framework_simplejwt',

    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Third party middleware. Corsheaders
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Third party middleware. Whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "allauth.account.middleware.AccountMiddleware", # Third party middleware. Allauth
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Create the static directory if it doesn't exist
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

neo_config.DATABASE_URL = (
    f'neo4j+s://neo4j:{config("GRAPH_PASSWORD")}@'
    f'{config("GRAPH_CONNECTION_URL").replace("neo4j+s://", "")}'
)

# Force SSL/TLS for Aura
neo_config.FORCE_SSL = True

NEO4J_URI = config('GRAPH_CONNECTION_URL')
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = config('GRAPH_PASSWORD')


# my_driver = GraphDatabase().driver(config('GRAPH_CONNECTION_URL'), auth=('neo4j', config('GRAPH_PASSWORD')))
# db.set_connection(driver=my_driver)

tmpPostgres = urlparse(config("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        
        
    }
}

AUTH_USER_MODEL = 'authentication.User'


REST_USE_JWT = True
JWT_AUTH_COOKIE = 'spirit-auth'
JWT_AUTH_REFRESH_COOKIE = 'spirit-refresh-token'


SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# Social Auth settings
SOCIALACCOUNT_ADAPTER = 'authentication.adapters.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'authentication.adapters.CustomAccountAdapter'

REACT_FRONTEND = config('REACT_FRONTEND')
DJANGO_BACKEND = config('DJANGO_BACKEND')

GOOGLE_OAUTH_CALLBACK_URL = config('GOOGLE_OAUTH_CALLBACK_URL')
CORS_ALLOWED_ORIGINS = [
    REACT_FRONTEND,  # React frontend
    DJANGO_BACKEND,  # Django backend
]

CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings that might help
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL')

ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY')