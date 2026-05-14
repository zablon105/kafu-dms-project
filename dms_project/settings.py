import os
import dj_database_url
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

"""
Django settings for dms_project project.
"""

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('SECRETE_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY environment variable must be set.')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']

# APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'documents',
    
    # NEW: For Supabase Storage
    'storages',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ correct position
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dms_project.urls'

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'dms_project.wsgi.application'

# DATABASE
DATABASE_URL = os.getenv('DATABASE_URL', '')
if not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL environment variable must be set.')

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
}

# Keeps Django checking dead DB connections automatically
CONN_HEALTH_CHECKS = True

# PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========== MEDIA FILES - SUPABASE STORAGE ==========
# NEW: Using Supabase Storage for uploaded documents

# Supabase Storage Configuration
SUPABASE_PROJECT_URL = os.getenv('SUPABASE_PROJECT_URL', 'https://xxtfvsrevwololmytkvu.supabase.co')
SUPABASE_BUCKET_NAME = os.getenv('SUPABASE_BUCKET_NAME', 'documents')

# S3-Compatible Storage (Supabase uses S3 API)
AWS_ACCESS_KEY_ID = os.getenv('SUPABASE_ACCESS_KEY', '')
AWS_SECRET_ACCESS_KEY = os.getenv('SUPABASE_SECRET_KEY', '')
AWS_STORAGE_BUCKET_NAME = SUPABASE_BUCKET_NAME
AWS_S3_ENDPOINT_URL = f"{SUPABASE_PROJECT_URL}/storage/v1/s3"
AWS_S3_REGION_NAME = os.getenv('SUPABASE_REGION', 'eu-west-2')
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False  # Don't add auth params to URLs
AWS_S3_FILE_OVERWRITE = False  # Don't overwrite files with same name
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Use S3 storage for uploaded files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Keep local media root as fallback (for development)
MEDIA_URL = f"{SUPABASE_PROJECT_URL}/storage/v1/object/public/{SUPABASE_BUCKET_NAME}/"
MEDIA_ROOT = BASE_DIR / 'media'  # Fallback for local development

# AUTH REDIRECTS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ========== EMAIL CONFIGURATION ==========
# For development - shows reset link in terminal
# For production, set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in Render environment variables

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Email settings (uses environment variables for security)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Fallback to console backend if no email credentials are provided
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'