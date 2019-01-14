from botocore.exceptions import ClientError
import boto3
import datetime

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
now = datetime.datetime.now()


def determine_buckets_to_remove(buckets, tags, context):
    buckets_to_remove = set()

    try:
        for bucket in buckets:
            bucket_tagging = s3_client.get_bucket_tagging(
                Bucket=bucket['Name']
            )
            context.log(f"Bucket: {bucket['Name']} has tags: {bucket_tagging['TagSet']}")

            for tagset in tags:
                if all([tag in bucket_tagging['TagSet'] for tag in tagset]):
                    buckets_to_remove.add(bucket['Name'])

    except ClientError as e:
        if e.response["Error"]["Code"] == 'NoSuchTagSet':
            pass

    return buckets_to_remove


def remove_buckets(buckets_to_remove, context):
    print(f'Buckets to be removed are: {buckets_to_remove}')

    for bucket in buckets_to_remove:
        context.log(f'Emptying bucket: {bucket}')
        bucket = s3_resource.Bucket(bucket)
        # bucket.objects.all().delete()

        context.log(f'Deleting bucket {bucket}')
        # bucket.delete()


def prepare_tags(event, context):
    tags = []

    for tags_dict in event:
        tagset = []
        for k, v in tags_dict.items():
            tagset.append({'Key': f'{k}', 'Value': f'{v}'})
        tags.append(tagset)

    context.log(f'The tags are ==> {tags}')
    return tags


def handler(event, context):
    try:
        context.log(f'The event is ==> {event}')
        buckets = s3_client.list_buckets()['Buckets']

        tags = prepare_tags(event, context)
        buckets_to_remove = determine_buckets_to_remove(buckets, tags, context)
        remove_buckets(buckets_to_remove, context)

        return {
            'statusCode': 200,
        }
    except ClientError as e:
        context.log(f'Unexpected client error: {e}')
        return {
            'statusCode': 400,
        }
