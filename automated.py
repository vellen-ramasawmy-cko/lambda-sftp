# Reference: https://checkout.atlassian.net/wiki/spaces/CHEC/pages/4396811491/034+-+Create+an+SFTP+account+on+AWS+for+NAS+Merchant+Reporting
# https://spin.atomicobject.com/2021/06/08/jq-creating-updating-json/
# https://www.py4u.net/discuss/1192644
# https://aws.amazon.com/blogs/storage/simplify-your-aws-sftp-structure-with-chroot-and-logical-directories/
# https://docs.aws.amazon.com/fr_fr/cli/latest/reference/transfer/create-user.html

# --tags unavailable, solution update awscli to latest version: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-upgrade
# aws cli version used 2.3.3

import boto3,json

#AWS account
session = boto3.Session(profile_name='cko-playground')

## Pre-checks

# Ensure that there are no Route 53 entries with the same name that are already present on cko-prod-legacy.
# Ensure that there are no AWS Transfer Family service entries with the same name that are already present on cko-prod-legacy.
# Ensure that there are no folder on S3 with the same name that are already present on cko-prod-legacy.

##  Variables
# Merchant name

#---------------s3 = session.client('s3')
#response = s3.list_buckets()

# Output the bucket names
#print('Existing buckets:')
#for bucket in response['Buckets']:
#    print(f'  {bucket["Name"]}')-------


print("")
print(">> Please note that this is the automation for SFTP Automated Reporting and Token Migration. <<\n")
print("IMPORTANT: Merchant Name is used for Token Migration and Merchant Account Id and Merchant Name is used for automated reporting:\n\
\n\
- New user on AWS Transfer Family -->  merchantid\n\
- Entry on Route53                -->  merchantname.sftp.checkout.com\n\
- S3 Bucket                       -->  sftp-aws-cko/merchantid\n\
")


#print("Enter the type of SFTP (Token or Automated): ")
ac_type=input("Enter the type of SFTP (Token or Automated): ")

if(ac_type == "token"):
    print("Token Account")
    merchantname=input("Enter merchant name to be used: ")
    s3folder=merchantname
    sftpuser=merchantname

elif(ac_type == "automated"):
    print("Automated Account")
    merchantname=input("Enter merchant name to be used: ")
    merchantid=input("Enter merchant account id to be used: ")
    s3folder=merchantid
    sftpuser=merchantid
else:
    exit()

#Validation
#----To be included

merchantnametag=input("Enter merchant name to be used as AWS Tags, e.g Curve OS Ltd: ")
changenumber=input("Enter the change number, e.g CHN-1234: ")
creator=input("Enter the creator name for AWS Tags, e.g Nirvan: ")
purpose=input("Enter the purpose of this change, e.g Automated Reporting: ")
requester=input("Enter the name of the requester, e.g Nirvan: ")
public_key=input("Enter the SSH Key: ")

print("\n")

if(ac_type == "token"):
    print("Merchant name to be used:" + merchantname)

if(ac_type == "automated"):
    print("Merchant name to be used:" + merchantname)
    print("Merchant id to be used:" + merchantid)


print(">> AWS Tag Used <<")

print("AWS Tag for merchant name: " + merchantnametag)
print("Change number: " + changenumber)
print("Creator: " + creator)
print("Purpose of this change: " + purpose)
print("Requester: " + requester)
print("SSH key: "+ public_key)

print("\n")
choice=input("Do you want to proceed with the SFTP Creation (Y OR N) ->  ")
print("\n")
if choice == "Y" or choice == "y":
    print("Proceeding with SFTP Creation of " + merchantname)
else:
    exit()

# Creation on AWS

#Variables
playground_server_id="s-a3c053263ced44f5b"
home_directory_mapping='Entry=/,Target=/sftp-test-nb/'+ s3folder
home_directory='/sftp-test-nb/'+ s3folder
role_arn="arn:aws:iam::528130383285:role/aws-sftp-nb-test"
policy_arn="arn:aws:iam::528130383285:policy/aws-sftp-policy-nb-test"
print("\n")
print(playground_server_id)
print(home_directory_mapping)
print(home_directory)
print(role_arn)
print(policy_arn)
print("\n")


# Creates Folder on S3 Bucket
print(">> Creating Folder on S3 Bucket <<")
s3 = session.client('s3')
s3.put_object(Bucket='vellen-sftp-test',Key=s3folder)

s3file=s3.get_object(Bucket='vellen-sftp-test',Key='policy.json')
json_content = s3file["Body"].read().decode()


# Creates User on AWS Transfer Family
print("\n")
print(">> Creating user on AWS Transfer Family <<")
transfer = session.client('transfer')
response = transfer.create_user(
    HomeDirectory=home_directory,
    Policy= json_content,
    Role=role_arn,
    ServerId= playground_server_id,
    SshPublicKeyBody=public_key,
    Tags=[
        {
            'Key': 'Change',
            'Value': changenumber
        },
        {
            'Key': 'Creator',
            'Value': creator
        },
        {
            'Key': 'Merchant',
            'Value': merchantnametag
        },
        {
            'Key': 'Purpose',
            'Value': purpose
        },
        {
            'Key': 'Requester',
            'Value': requester
        },
    ],
    UserName=sftpuser
)

print(response)


# Creates route 53 records 

print(">> Creating Route 53 record <<")
dns=playground_server_id +".server.transfer.eu-west-1.amazonaws.com"