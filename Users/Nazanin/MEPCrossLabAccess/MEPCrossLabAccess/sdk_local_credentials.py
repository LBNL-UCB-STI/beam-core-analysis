import boto3
import json

# start a session connecting to AWS Lambda
session = boto3.Session(profile_name="ace")
client = session.client('lambda')

# load the test file
payload = "2022-05-05-beam-smart1-sf-baseline-ace.json"
with open(payload, 'r') as f:
    data = f.read()

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
