from lambdas import s3_cleanup
from mock import patch

ALL_BUCKETS = [
    {'Name':'binx-cleanup-lambda'},
    {'Name':'binx-s3-cleanup-bucket1'},
    {'Name':'binx-s3-cleanup-bucket2'},
    {'Name':'binx-s3-cleanup-bucket3'},
    {'Name':'binx-s3-cleanup-bucket4'},
    {'Name':'binx-s3-cleanup-bucket5'},
    {'Name':'binx-s3-cleanup-bucket6'},
    {'Name':'binx-s3-cleanup-bucket7'},
    {'Name':'binx-s3-cleanup-bucket8'}
]


def mock_get_tags(bucket_name):
    tagsets = {
        'binx-cleanup-lambda': [
            {'Key': 'aws:cloudformation:stack-id', 'Value': 'arn:aws:cloudformation:eu-west-1:569769687575:stack/binx-s3-cleanup-binx-eu-bucket/791acd30-1992-11e9-9c1c-0254d350c81a'},
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-bucket'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'DeployBucket'}
        ],
        'binx-s3-cleanup-bucket1': [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket1'},
            {'Key': 'at', 'Value': 'deploy'},
            {'Key': 'aws:cloudformation:stack-id', 'Value': 'arn:aws:cloudformation:eu-west-1:569769687575:stack/binx-s3-cleanup-binx-eu-ocp-buckets/66bec2b0-1995-11e9-979b-06bacc45a76c'}
        ],
        'binx-s3-cleanup-bucket2': [
            {'Key':'owner','Value':'ocp'},
            {'Key':'aws:cloudformation:stack-name','Value':'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key':'aws:cloudformation:logical-id','Value':'Bucket2'},
            {'Key':'at','Value':'delete'},
            {'Key':'aws:cloudformation:stack-id','Value':'arn:aws:cloudformation:eu-west-1:569769687575:stack/binx-s3-cleanup-binx-eu-ocp-buckets/66bec2b0-1995-11e9-979b-06bacc45a76c'}
        ],
        'binx-s3-cleanup-bucket3': [
           {'Key': 'owner', 'Value': 'ocp'},
           {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
           {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket3'},
           {'Key': 'aws:cloudformation:stack-id', 'Value': 'arn:aws:cloudformation:eu-west-1:569769687575:stack/binx-s3-cleanup-binx-eu-ocp-buckets/66bec2b0-1995-11e9-979b-06bacc45a76c'}
       ],
        'binx-s3-cleanup-bucket4': [
            {'Key': 'owner', 'Value': 'bojack'},
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket4'},
            {'Key': 'aws:cloudformation:stack-id', 'Value': 'arn:aws:cloudformation:eu-west-1:569769687575:stack/binx-s3-cleanup-binx-eu-ocp-buckets/66bec2b0-1995-11e9-979b-06bacc45a76c'}
        ],
        'binx-s3-cleanup-bucket5': [
            {'Key': 'aws:cloudformation:stack-id', 'Value': 'arn:aws:cloudformation:eu-west-1:569769687575:stack/binx-s3-cleanup-binx-eu-ocp-buckets/66bec2b0-1995-11e9-979b-06bacc45a76c'},
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket5'}
        ],
        'binx-s3-cleanup-bucket6': [
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket6'},
            {'Key':'prod', 'Value':'delete'}
        ],
        'binx-s3-cleanup-bucket7': [
            {'Key': 'owner', 'Value': 'roadrunner'},
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket7'},
            {'Key':'prod', 'Value':'delete'}
        ],
        'binx-s3-cleanup-bucket8': [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'aws:cloudformation:stack-name', 'Value': 'binx-s3-cleanup-binx-eu-ocp-buckets'},
            {'Key': 'aws:cloudformation:logical-id', 'Value': 'Bucket7'},
            {'Key':'prod', 'Value':'delete'}
        ]
    }
    return tagsets[bucket_name]


@patch('lambdas.s3_cleanup.get_tags', mock_get_tags)
def test_determine_buckets_to_remove_with_no_match():
    tags = [
        [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'no', 'Value': 'match'}
        ]
    ]
    buckets_to_be_removed = s3_cleanup.determine_buckets_to_remove(ALL_BUCKETS, tags)

    assert buckets_to_be_removed == set()


@patch('lambdas.s3_cleanup.get_tags', mock_get_tags)
def test_determine_buckets_to_remove_with_single_tagset_match():
    tags = [
        [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'at', 'Value': 'delete'}
        ]
    ]
    buckets_to_be_removed = s3_cleanup.determine_buckets_to_remove(ALL_BUCKETS, tags)

    assert buckets_to_be_removed == {'binx-s3-cleanup-bucket2'}


@patch('lambdas.s3_cleanup.get_tags', mock_get_tags)
def test_determine_buckets_to_remove_with_multiple_tagset_matches():
    tags = [
        [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'at', 'Value': 'delete'}
        ],
        [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'prod', 'Value': 'delete'}
        ]
    ]
    buckets_to_be_removed = s3_cleanup.determine_buckets_to_remove(ALL_BUCKETS, tags)

    assert buckets_to_be_removed == {'binx-s3-cleanup-bucket2', 'binx-s3-cleanup-bucket8'}


def test_process_empty_tags():
    input_tags1 = []
    assert s3_cleanup.process_tags(input_tags1) == []


def test_process_single_tag():
    input_tags2 = [
        {'hello': 'world'}
    ]
    assert s3_cleanup.process_tags(input_tags2) == [
        [
            {'Key': 'hello', 'Value': 'world'}
        ]
    ]


def test_process_multiple_tags():
    input_tags3 = [
        {'owner': 'ocp', 'at': 'delete'},
        {'owner': 'ocp', 'prod': 'delete'}
    ]
    assert s3_cleanup.process_tags(input_tags3) == [
        [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'at', 'Value': 'delete'}
        ],
        [
            {'Key': 'owner', 'Value': 'ocp'},
            {'Key': 'prod', 'Value': 'delete'}
        ]
    ]
