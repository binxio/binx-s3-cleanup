## Binx Scheduled Tag-Based S3 Bucket Clean-up Lambda

A configurable Lambda that looks through S3 buckets at a scheduled interval and empties and 
then deletes S3 buckets that are tagged for deletion. The tags that must exist on the bucket are
customizable via the CloudFormation template using the event input section.

The tags can be defined using a simplified format which looks as follows: 
```
'[
  {
    "owner": "jimmy"
  },
  {
    "owner": "bob",
    "testing": "delete"
  }
]'
```

Before using the tags to determine which buckets should be removed the Lambda will translate this 
into the tagging format expected by AWS. for example, the above would be translated to:

```
[
    [
        {'Key': 'owner', 'Value': 'jimmy'}
    ],
    [
        {'Key': 'owner', 'Value': 'bob'},
        {'Key': 'testing', 'Value': 'delete'}
    ]
]
``` 

In this example the lambda will delete any bucket that has the tag `{'Key': 'owner', 'Value': 'jimmy'}`
and any buckets that has both the `{'Key': 'owner', 'Value': 'bob'}` and `{'Key': 'testing', 'Value': 'delete'}` tags.

The schedule is also customizable through the CloudFormation template by changing the rate of the schedule property.

These properties are both located in the Lambda event shown below: 
```
Events:
    DailySchedule:
      Type: Schedule
      Properties:
        Schedule: rate(1 day)
        Input: '[
                  {
                    "owner": "bob",
                    "at": "delete"
                  },
                  {
                    "owner": "bob",
                    "prod": "delete"
                  }
                ]'
```