import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dms_project.settings')
import django
django.setup()
from django.conf import settings
print('USE_SUPABASE_STORAGE=', getattr(settings,'USE_SUPABASE_STORAGE',None))
print('AWS_ACCESS_KEY_ID=', bool(getattr(settings,'AWS_ACCESS_KEY_ID',None)))
print('AWS_SECRET_ACCESS_KEY=', bool(getattr(settings,'AWS_SECRET_ACCESS_KEY',None)))
print('AWS_STORAGE_BUCKET_NAME=', getattr(settings,'AWS_STORAGE_BUCKET_NAME',None))
print('SUPABASE_PROJECT_URL=', getattr(settings,'SUPABASE_PROJECT_URL',None))
print('MEDIA_ROOT=', getattr(settings,'MEDIA_ROOT',None))
