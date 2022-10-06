import boto3
import sys

# list, clear and delete all buckets
s3 = boto3.resource('s3')
bucket_list = s3.buckets.all()
print('Deleting all buckets...')
for bucket in bucket_list:
    print('Deleting bucket: ' + bucket.name)
    bucket.objects.all().delete()
    bucket.delete()
print('All buckets successfully deleted.')