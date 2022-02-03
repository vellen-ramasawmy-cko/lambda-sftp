import boto3,json,urllib.request
session = boto3.Session(profile_name='cko-playground')


s3 = session.client('s3')


s3file=s3.get_object(Bucket='vellen-sftp-test',Key='policy.json')
json_content = s3file["Body"].read().decode()
#json.loads(text)

print(json_content)
