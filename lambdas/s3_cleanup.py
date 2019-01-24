from botocore.exceptions import ClientError
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')


def determine_buckets_to_remove(buckets, tags):
    buckets_to_remove = set()

    for bucket in buckets:
        bucket_tagging = get_tags(bucket['Name'])

        for tagset in tags:
            if all([tag in bucket_tagging for tag in tagset]):
                buckets_to_remove.add(bucket['Name'])

    return buckets_to_remove


def get_tags(bucket_name) -> [dict]:
    try:
        return s3_client.get_bucket_tagging(Bucket=bucket_name)['TagSet']
    except ClientError as e:
        if e.response["Error"]["Code"] == 'NoSuchTagSet':
            return []


def all_buckets():
    try:
        return s3_client.list_buckets()['Buckets']
    except ClientError as e:
        logger.error(f'Unexpected client error: {e}')
        return {
            'statusCode': 400,
        }


def remove_buckets(buckets_to_remove):
    for bucket in buckets_to_remove:
        logger.info(f'Emptying and deleting bucket: {bucket}')
        bucket = s3_resource.Bucket(bucket)
        bucket.objects.all().delete()
        bucket.delete()


def add_deletion_lifecyle_policy_to_buckets(buckets_to_remove):
    for bucket in buckets_to_remove:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'Expiration': {
                            'Date': 1
                        },
                        'ID': 'empty_old_buckets_policy',
                        'Filter': {
                            'Prefix': '*'
                        },
                        'Status': 'Disabled',
                        'AbortIncompleteMultipartUpload': {
                            'DaysAfterInitiation': 1
                        }
                    },
                ]
            }
        )


def process_tags(event):
    tags = []

    for tags_dict in event:
        tagset = []
        for k, v in tags_dict.items():
            tagset.append({'Key': f'{k}', 'Value': f'{v}'})
        tags.append(tagset)

    return tags


def handler(event, _):
    try:
        buckets = all_buckets()
        tags = process_tags(event)
        buckets_to_remove = determine_buckets_to_remove(buckets, tags)
        add_deletion_lifecyle_policy_to_buckets(buckets_to_remove)
        # remove_buckets(buckets_to_remove)

        return {
            'statusCode': 200,
        }
    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}')
