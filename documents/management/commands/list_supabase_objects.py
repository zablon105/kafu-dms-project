from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'List objects in the configured Supabase storage bucket (uses Django settings)'

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='', help='Prefix to filter objects')
        parser.add_argument('--max', type=int, default=1000, help='Maximum objects to list')

    def handle(self, *args, **options):
        prefix = options['prefix']
        max_keys = options['max']

        endpoint = getattr(settings, 'AWS_S3_ENDPOINT_URL', None) or f"{getattr(settings, 'SUPABASE_PROJECT_URL', '')}/storage/v1/s3"
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None) or getattr(settings, 'SUPABASE_BUCKET_NAME', None)

        if not bucket:
            self.stderr.write('Bucket name not configured in settings (AWS_STORAGE_BUCKET_NAME / SUPABASE_BUCKET_NAME)')
            return

        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)

        if not access_key or not secret_key:
            self.stderr.write('S3 credentials missing in settings (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)')
            return

        cfg = Config(signature_version=getattr(settings, 'AWS_S3_SIGNATURE_VERSION', 's3v4'),
                     s3={'addressing_style': getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'path')})
        client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                              endpoint_url=endpoint, region_name=getattr(settings, 'AWS_S3_REGION_NAME', None),
                              config=cfg)

        try:
            paginator = client.get_paginator('list_objects_v2')
            page_iter = paginator.paginate(Bucket=bucket, Prefix=prefix, PaginationConfig={'MaxItems': max_keys})
            total = 0
            for page in page_iter:
                for obj in page.get('Contents', []):
                    total += 1
                    self.stdout.write(obj['Key'])
            if total == 0:
                self.stdout.write('No objects found (or insufficient permissions).')
            else:
                self.stdout.write(self.style.SUCCESS(f'Listed {total} objects.'))
        except ClientError as e:
            err = e.response.get('Error', {})
            self.stderr.write(f"S3 error: {err.get('Code')} {err.get('Message')}")
