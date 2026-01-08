import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-gnyankbr5(8zu3u!$1996czbu5en2stm#eobw2oeymzmmj2g=c')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'django_filters',
    'import_export',
    'debug_toolbar',
    
    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.products',
    'apps.orders',
    'apps.shop_cart',
]

# Email settings for password reset
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
# For production, you'll want to configure a real email backend

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'coffee_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.products.context_processors.categories',
                'apps.shop_cart.context_processors.cart',
            ],
        },
    },
]

# Cart settings
CART_SESSION_ID = 'cart'

WSGI_APPLICATION = 'coffee_shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Настройки PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'coffee_shop'),
        'USER': os.environ.get('POSTGRES_USER', 'coffee_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'coffee_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5434'),
    }
}

# Redis/Celery settings
CELERY_BROKER_URL = f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0"
CELERY_RESULT_BACKEND = f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Настройки языка и перевода
LANGUAGE_CODE = 'ru-ru'

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

# Директории с переводами
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Временная зона
TIME_ZONE = 'Europe/Moscow'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Login/Logout URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'products:product_list'
LOGOUT_REDIRECT_URL = 'products:product_list'

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
CART_SESSION_ID = 'cart'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# Debug Toolbar settings
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Ensure the debug toolbar is only shown in debug mode
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
