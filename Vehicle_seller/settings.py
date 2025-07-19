from pathlib import Path
import os
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

BASE_DIR = Path(__file__).resolve().parent.parent

# Security: Use environment variable for SECRET_KEY, no fallback
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

DEBUG = os.getenv('DEBUG', 'False') == 'True'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # Add environment detection

# Update ALLOWED_HOSTS for production
if ENVIRONMENT == 'production':
    ALLOWED_HOSTS = [
        'dms-g5l7.onrender.com',
        '*.dms-g5l7.onrender.com',
        'your-domain.com',  # Replace with your actual domain
        '*.your-domain.com',
    ]
else:
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '.localhost',
        'dms-g5l7.onrender.com',
        '*.dms-g5l7.onrender.com',
    ]

ROOT_URLCONF = 'Vehicle_seller.urls'
TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"

SHARED_APPS = [
    'django_tenants',
    'tenants',
    'accounts',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

TENANT_APPS = [
    'dealership',
]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS
SITE_ID = 1
DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']
AUTH_USER_MODEL = 'accounts.CustomUser'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_tenants.middleware.main.TenantMainMiddleware',
    'tenants.middleware.TenantIdentificationMiddleware',  # Updated path
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.CustomSessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# Update CORS settings for production
if ENVIRONMENT == 'production':
    CORS_ALLOWED_ORIGINS = [
        "https://dms-frontend-vite-kvhm.vercel.app",
        "https://dms-g5l7.onrender.com",
        "https://your-domain.com",  # Your main domain
        "https://dealership1.your-domain.com",  # Subdomain examples
        "https://dealership2.your-domain.com",
    ]
    
    CSRF_TRUSTED_ORIGINS = [
        "https://dms-frontend-vite-kvhm.vercel.app",
        "https://dms-g5l7.onrender.com",
        "https://your-domain.com",
        "https://*.your-domain.com",
    ]
    
    SESSION_COOKIE_DOMAIN = '.your-domain.com'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Development settings
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://dms-frontend-vite-kvhm.vercel.app",
    ]
    
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://dms-frontend-vite-kvhm.vercel.app",
    ]
    
    SESSION_COOKIE_DOMAIN = '.localhost'
    SESSION_COOKIE_SECURE = False

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-csrftoken',
    'x-session-id',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SAMESITE = 'None' if ENVIRONMENT == 'production' else 'Lax'
SESSION_COOKIE_AGE = 1209600

CSRF_COOKIE_SAMESITE = 'None' if ENVIRONMENT == 'production' else 'Lax'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True}},
}

WSGI_APPLICATION = 'Vehicle_seller.wsgi.application'

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        engine='django_tenants.postgresql_backend',
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
                'accounts.context_processors.tenant_context',
            ],
        },
    },
]