# MEP Run examples

These examples show how to invoke the mep-run lambda, using either the [AWS CLI](https://aws.amazon.com/cli/) or
the [AWS SDK for Python (known as boto3)](https://aws.amazon.com/sdk-for-python/). 

The referenced file should have it's "user" section filled out appropriately.

Once the lambda is invoked, the following will occur:
  1. a few seconds will pass by, more if it's been a while since the last MEP request (cold start)
  2. if there was an issue with your connection to AWS, you will raise an exception
  3. if there was an issue with your mep job, that will be found in the response body
  4. if there were no errors validating your MEP request, the job will be queued

    - a job may remain enqueued for a while as clusters are spun up or other jobs are run
  5. you will receive an email when your job begins running on the cluster
  6. you will receive either a SUCCESS or FAILURE email depending on the outcome of running your job

    - for now, you will receive 2 failure emails if a failure occurs during the search phase of the app
    - the success email has a high-level summary of the result
    - no plots yet (coming soon)

### AWS CLI using local AWS credentials

```bash
$ aws lambda invoke \
  --function-name mep-run \
  --cli-binary-format raw-in-base64-out \
  --payload file://2022-05-05-beam-smart1-sf-baseline-ace.json \
  response.json
```

### AWS SDK for Python (boto3) using local aws credentials

```python
import boto3
import json

# start a session connecting to AWS Lambda
session = boto3.Session(profile_name="ace")
client = session.client('lambda')

# load the test file
#payload = "2022-05-05-beam-smart1-sf-baseline-ace.json"
payload = "test.json"
with open(payload, 'r') as f:
    data = f.read()

# send the request to invoke the lambda
response = client.invoke(
    FunctionName='mep-dev-mep-validation',
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=data
)

# read the response
res_bytes = response['Payload'].read()
res_json = json.loads(res_bytes.decode("utf-8"))
print(json.dumps(res_json, sort_keys=True, indent=4))
```

### AWS SDK for Python (boto3) using assumed role

```python
import boto3
import base64

sts = boto3.client('sts')

payload_file = "2022-05-05-beam-smart1-sf-baseline-ace.json"
with open(payload_file, 'r') as f:
    data = f.read()

assumed_role_object = sts.assume_role(
    RoleArn=f"arn:aws:iam::991404956194:role/mep-cross-lab-access",
    ExternalId="a5YmC5Lb26gD",
    RoleSessionName='test')

credentials = assumed_role_object['Credentials']

session = boto3.Session(
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
)

#session = boto3.Session()
client = session.client('lambda')

# send the request to invoke the lambda
response = client.invoke(
    FunctionName='mep-dev-mep-validation',
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=data
)

# read the response
res_bytes = response['Payload'].read()
res_json = json.loads(res_bytes.decode("utf-8"))
print(json.dumps(res_json, sort_keys=True, indent=4))
```

