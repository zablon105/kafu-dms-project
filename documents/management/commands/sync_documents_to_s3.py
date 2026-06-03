from django.core.management.base import BaseCommand
from django.conf import settings
from documents.models import Document
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import os


class Command(BaseCommand):
    help = 'Sync local Document files to Supabase S3 when the object is missing. Dry-run by default.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Perform uploads instead of dry-run')
        parser.add_argument('--prefix', default='', help='Only consider DB file paths containing this substring')

    def handle(self, *args, **options):
        do_apply = options['apply']
        only_if = options['prefix']

        endpoint = getattr(settings, 'AWS_S3_ENDPOINT_URL', None) or f"{getattr(settings, 'SUPABASE_PROJECT_URL', '')}/storage/v1/s3"
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None) or getattr(settings, 'SUPABASE_BUCKET_NAME', None)
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)

        if not bucket or not access_key or not secret_key:
            self.stderr.write('Missing S3 configuration in settings. Set AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY')
            return

        cfg = Config(signature_version=getattr(settings, 'AWS_S3_SIGNATURE_VERSION', 's3v4'),
                     s3={'addressing_style': getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'path')})
        s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                          endpoint_url=endpoint, region_name=getattr(settings, 'AWS_S3_REGION_NAME', None), config=cfg)

        docs = Document.objects.all()
        to_upload = []
        for doc in docs:
            key = doc.file.name
            if only_if and only_if not in key:
                continue
            try:
                s3.head_object(Bucket=bucket, Key=key)
                # exists
            except ClientError as e:
                code = e.response.get('Error', {}).get('Code', '')
                if code in ('404', 'NoSuchKey', 'NotFound'):
                    local_path = None
                    if hasattr(doc.file, 'path'):
                        local_path = doc.file.path
                    if local_path and os.path.exists(local_path):
                        to_upload.append((doc.id, key, local_path))
                    else:
                        self.stdout.write(f'missing object and no local file: id={doc.id} key={key}')
                else:
                    self.stderr.write(f'Error checking key {key}: {e}')

        if not to_upload:
            self.stdout.write('No missing objects found that have local files to upload.')
            return

        self.stdout.write(f'Found {len(to_upload)} missing objects with local files.')
        for doc_id, key, local_path in to_upload:
            self.stdout.write(f'id={doc_id} key={key} file={local_path}')
        if do_apply:
            for doc_id, key, local_path in to_upload:
                with open(local_path, 'rb') as fh:
                    extra = getattr(settings, 'AWS_S3_OBJECT_PARAMETERS', None) or {}
                    s3.upload_fileobj(fh, bucket, key, ExtraArgs=extra)
                    self.stdout.write(f'Uploaded id={doc_id} -> {key}')
            self.stdout.write(self.style.SUCCESS(f'Uploaded {len(to_upload)} files.'))
        else:
            self.stdout.write('Dry-run complete. Re-run with --apply to upload files.')
