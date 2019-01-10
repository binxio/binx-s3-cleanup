import boto3
import datetime

s3_client = boto3.client('s3')
now = datetime.datetime.now()


def handler(event, context):
    buckets = s3_client.list_buckets()

    print(f'All buckets ====> {buckets}')

    return {
        'statusCode': 200,
    }