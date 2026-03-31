
from datetime import timedelta
from pathlib import Path

from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # Local
    'accounts',
    'warehouse',
    'customer',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'





# Ozim jaratqan user modelin tanistirdim
AUTH_USER_MODEL = 'accounts.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'    # model ushun ID-lar 64 bitlik ulken boliwi ushin


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [     # cookie ushin, qosildi toeknlerge 
        'accounts.authentication.CookieJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'EXCEPTION_HANDLER': 'core.exception_handler.custom_exception_handler',
}




# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


ACCESS_TOKEN_COOKIE = 'access_token'
REFRESH_TOKEN_COOKIE = 'refresh_token'



# drf-spectacular (Swagger / OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Online Market API',
    'DESCRIPTION': 'REST API for Online Market',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # swaggerdin yaml sxema fayli ushin API-di oshirip qoyadi. API qatarinda ko'rinbeydi
    'SECURITY': [{'CookieAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'CookieAuth': {
                'type': 'apiKey',   # token turi
                'in': 'cookie',     # cookie-den izlew kerek ekin bildiredi yamasa saqlaw kerek ekenin
                'name': 'access_token',     # token saqlaniwshi ozgeriwshi ati
            },
        },
    },
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,   # kiritilgen login magluwmatlardi, browser localStorage saqlaw ruqsat beredi
        'requestInterceptor': 'function(req) { req.credentials = "include"; return req; }', # req.credentials = "include" - api request-ge browser famitinda saqlap qoygan kerekli cookie-lardi qosip jiberedi
    },  
    'TAGS': [
        {'name': 'Auth', 'description': 'Login, logout, token refresh'},
        {'name': 'Profile', 'description': 'user: create, delete, patch, get'},
    ],
}




# Production security
""" servrede qawipsizlik ushin jazilgan """
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())   # isenimli domenler dizimi. CSRF-den qorgaw ushin. cookie uralaniwin aldin aladi.

if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)    # http-di majburiy https-ke aylandiradi
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True    # tek HTTPS arqali cookie jiberiwdi bildiredi
    CSRF_COOKIE_SECURE = True   # tek HTTPS arqali cookie jiberiwdi bildiredi
    SECURE_HSTS_SECONDS = 31536000  # 1 jilda sekun islewin bildiredi, 365 kun
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # sub domenlergeda tiyisli kun islewi
    SECURE_HSTS_PRELOAD = True  # browserlardin tek https qosiw bildiredi
    SECURE_CONTENT_TYPE_NOSNIFF = True  # MIME Sniffing degen hujimden qorganiw, jasirin JavaScript kodlardi, yamasa basqa kodlar, browserde avtomat run bolip ketiwden qorgaydi
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',    # tek JSON qayatriw ushin, "Browsable API"di oshiredi, API duzilisin ko'rmew ushin
    ]

