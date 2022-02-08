from multiprocessing.sharedctypes import Value
import boto3,json,urllib.request
session = boto3.Session(profile_name='cko-playground')


s3 = session.client('s3')


s3file=s3.get_object(Bucket='vellen-sftp-test',Key='record.json')
json_content = s3file["Body"].read().decode()
a=json.loads(json_content)
str_replace_name=a["Changes"][0]["ResourceRecordSet"]["Name"]
str_replace_dns=a["Changes"][0]["ResourceRecordSet"]["ResourceRecords"][0]["Value"]

a["Changes"][0]["ResourceRecordSet"]["Name"] = str_replace_name.replace("target.company.com","sftpython.cko-playground.ckotech.co")

a["Changes"][0]["ResourceRecordSet"]["ResourceRecords"][0]["Value"] = str_replace_dns.replace("DNS", "s-e1027b976d2b4e67b.server.transfer.eu-west-1.amazonaws.com")

#print(a)


client = session.client('route53')

response = client.change_resource_record_sets(ChangeBatch=a,HostedZoneId="Z08800003NARTIMTZS14F")
print(response)


