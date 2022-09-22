import boto3
import base64
import json

sts = boto3.client('sts')

payload_file = "2022-05-05-beam-smart1-sf-baseline-ace.json"
with open(payload_file, 'r') as f:
    data = f.read()

assumed_role_object = sts.assume_role(
    RoleArn=f"arn:aws:iam::991404956194:role/mep-cross-lab-access",
    ExternalId="jafijk887fk88hj0n",
    RoleSessionName='haitam')

credentials = assumed_role_object['Credentials']

session = boto3.Session(
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
)

#session = boto3.Session()
client = session.client('lambda', region_name='us-west-2')

# send the request to invoke the lambda
response = client.invoke(
    FunctionName='mep-run',
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=data
)

# read the response
res_bytes = response['Payload'].read()
res_json = json.loads(res_bytes.decode("utf-8"))
print(json.dumps(res_json, sort_keys=True, indent=4))
