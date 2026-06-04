#!/usr/bin/env python
"""
Simple script to sync local media documents to Supabase S3 storage.
"""
import os
import boto3
from pathlib import Path

# Supabase/S3 Configuration
SUPABASE_ACCESS_KEY = os.getenv('SUPABASE_ACCESS_KEY')
SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')
SUPABASE_PROJECT_URL = os.getenv('SUPABASE_PROJECT_URL', 'https://xxtfvsrevwololmytkvu.supabase.co')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', f"{SUPABASE_PROJECT_URL}/storage/v1/s3")
BUCKET_NAME = 'documents'
LOCAL_MEDIA_DIR = Path('media/documents')

def create_s3_client():
    """Create S3 client for Supabase."""
    return boto3.client(
        's3',
        endpoint_url=AWS_S3_ENDPOINT_URL,
        aws_access_key_id=SUPABASE_ACCESS_KEY,
        aws_secret_access_key=SUPABASE_SECRET_KEY,
        region_name='eu-west-2',
        config=boto3.session.Config(signature_version='s3v4'),
    )

def main():
    if not SUPABASE_ACCESS_KEY or not SUPABASE_SECRET_KEY:
        print("❌ Missing SUPABASE_ACCESS_KEY or SUPABASE_SECRET_KEY")
        return
    
    s3_client = create_s3_client()
    
    # List existing objects in bucket
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='documents/')
        existing_keys = {obj['Key'] for obj in response.get('Contents', [])}
        print(f"📦 Found {len(existing_keys)} existing objects in S3 bucket")
    except Exception as e:
        print(f"❌ Error listing bucket: {e}")
        return
    
    # Get list of local files
    if not LOCAL_MEDIA_DIR.exists():
        print(f"❌ Local media directory not found: {LOCAL_MEDIA_DIR}")
        return
    
    local_files = list(LOCAL_MEDIA_DIR.glob('*'))
    print(f"📁 Found {len(local_files)} files locally")
    
    uploaded_count = 0
    skipped_count = 0
    failed_count = 0
    
    for local_file in local_files:
        if local_file.is_dir():
            continue
        
        # Create S3 key
        s3_key = f"documents/{local_file.name}"
        
        if s3_key in existing_keys:
            print(f"⏭️  Skipping (exists): {s3_key}")
            skipped_count += 1
            continue
        
        # Upload file
        try:
            s3_client.upload_file(
                str(local_file),
                BUCKET_NAME,
                s3_key,
            )
            print(f"✅ Uploaded: {s3_key}")
            uploaded_count += 1
        except Exception as e:
            print(f"❌ Failed to upload {s3_key}: {e}")
            failed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Uploaded: {uploaded_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Failed: {failed_count}")

if __name__ == '__main__':
    main()
