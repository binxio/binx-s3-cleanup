from botocore.exceptions import ClientError
import boto3
import datetime

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
now = datetime.datetime.now()


def determine_buckets_to_remove(buckets):
    buckets_to_remove = []

    try:
        for bucket in buckets:
            bucket_tagging = s3_client.get_bucket_tagging(
                Bucket=bucket['Name']
            )
            print(f"Bucket: {bucket['Name']} has tags: {bucket_tagging['TagSet']}")

            owner_tag = {'Key': 'owner', 'Value': 'ocp'}
            at_tag = {'Key': 'at', 'Value': 'delete'}
            prod_tag = {'Key': 'prod', 'Value': 'delete'}

            if owner_tag in bucket_tagging['TagSet']:
                print('Owner tags found!')
                if at_tag in bucket_tagging['TagSet'] or prod_tag in bucket_tagging['TagSet']:
                    print(f"Adding bucket: {bucket['Name']} to removal list")
                    buckets_to_remove.append(bucket['Name'])
    except ClientError as e:
        if e.response["Error"]["Code"] == 'NoSuchTagSet':
            pass

    return buckets_to_remove


def remove_buckets(buckets_to_remove):
    print(f'Buckets to be removed are: {buckets_to_remove}')

    for bucket in buckets_to_remove:
        print(f'Emptying bucket: {bucket}')
        bucket = s3_resource.Bucket(bucket)
        bucket.objects.all().delete()

        print(f'Deleting bucket {bucket}')
        bucket.delete()

    print(f'Done removing buckets')


def handler(event, context):
    try:
        buckets = s3_client.list_buckets()['Buckets']

        print(f'All buckets ====> {buckets}')

        buckets_to_remove = determine_buckets_to_remove(buckets)
        remove_buckets(buckets_to_remove)

        return {
            'statusCode': 200,
        }
    except ClientError as e:
        print(f'Unexpected client error: {e}')
        return {
            'statusCode': 400,
        }
    except Exception as e:
        print(f'Something went horribly wrong: {e}')
        return {
            'statusCode': 400,
        }
