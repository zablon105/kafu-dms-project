import os
import dj_database_url
from pathlib import Path

"""
Django settings for dms_project project.
"""

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY')
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
    'storages',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL', "postgresql://postgres.xxtfvsrevwololmytkvu:Kinzi%40%400023@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"),
        conn_max_age=600,
        ssl_require=True
    )
}

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
# Supabase Storage Configuration
SUPABASE_PROJECT_URL = os.getenv('SUPABASE_PROJECT_URL', 'https://xxtfvsrevwololmytkvu.supabase.co')
SUPABASE_BUCKET_NAME = os.getenv('SUPABASE_BUCKET_NAME', 'documents')

# S3-Compatible Storage (Supabase uses S3 API)
# IMPORTANT: These MUST be set in Render environment variables
AWS_ACCESS_KEY_ID = os.getenv('SUPABASE_ACCESS_KEY', '')
AWS_SECRET_ACCESS_KEY = os.getenv('SUPABASE_SECRET_KEY', '')
AWS_STORAGE_BUCKET_NAME = SUPABASE_BUCKET_NAME
AWS_S3_ENDPOINT_URL = f"{SUPABASE_PROJECT_URL}/storage/v1/s3"
AWS_S3_REGION_NAME = os.getenv('SUPABASE_REGION', 'eu-west-2')
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Only use S3 storage if keys are provided, otherwise fallback to local storage
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f"{SUPABASE_PROJECT_URL}/storage/v1/object/public/{SUPABASE_BUCKET_NAME}/"
    print(f"✅ Using Supabase Storage with bucket: {SUPABASE_BUCKET_NAME}")
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    print("⚠️ WARNING: Supabase credentials missing! Using local storage.")

MEDIA_ROOT = BASE_DIR / 'media'

# AUTH REDIRECTS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ========== EMAIL CONFIGURATION ==========
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'