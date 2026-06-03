import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Supabase storage S3 endpoint (storage subdomain)
endpoint = 'https://xxtfvsrevwololmytkvu.storage.supabase.co/storage/v1/s3'
# Bucket name
bucket = 'documents'
# Access keys (from your Render env screenshot). Keep them private; errors will be reported generally.
access_key = '71a3fcf7c5ee22cdb195721171626ff'
secret_key = 'f48154f04eba3febbf97d4b5974776beb0de4be5dac2fb0323c1dc945018b77'

s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                  endpoint_url=endpoint, region_name='eu-west-2',
                  config=Config(signature_version='s3v4', s3={'addressing_style':'path'}))

try:
    resp = s3.list_objects_v2(Bucket=bucket, Prefix='', MaxKeys=1000)
    print('KeyCount:', resp.get('KeyCount'))
    if resp.get('Contents'):
        for obj in resp['Contents']:
            print(obj['Key'])
    else:
        print('No objects found or insufficient permission to list.')
except ClientError as e:
    err = e.response.get('Error', {})
    print('ERROR', err.get('Code'), err.get('Message'))
except Exception as e:
    print('ERROR', str(e))
