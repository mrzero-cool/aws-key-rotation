import boto3, os, time, datetime, sys
from datetime import date
import array as arr
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')

db_client = boto3.client('dynamodb', region_name = 'ap-south-1')

db_resource = boto3.resource('dynamodb')

db_table = db_resource.Table('Users-List-IAM')

iam_users_list = iam_client.list_users()['Users'] 

ses_client = boto3.client('ses', region_name='ap-south-1') 

emailIdArr = []             
 
def create_users_list(tag, keyvalue, user_details):
    accesskeydate = keyvalue['CreateDate'].date()
    currentdate = date.today()
    active_days = currentdate - accesskeydate
    data = db_table.put_item(
       Item={
            "userName" : user_details['UserName'],
            "userId": user_details['UserId'],
            "currentAccessKey": keyvalue['AccessKeyId'],
            "keyActiveDays": active_days.days,
            "emailId": tag['Value'],
            "newAccessKey": 'Null',
        }
    )
    # print('User added successfully')
    
def email_multiple_keys_user(emailId):
        try:
            # ses_client.verify_email_address(EmailAddress = 'security@clouddestinations.com')
            # resp = ses_client.verify_email_address(EmailAddress = emailId)
            sender = 'security@clouddestinations.com'
            receiver = emailId
            res = ses_client.send_email(
                Source= sender,
                Destination={
                    'ToAddresses': [receiver]
                },
                Message={
                    'Subject': {
                        'Data': 'Multiple Access Keys in USe',
                        'Charset': 'utf-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': 'Your AWS IAM account has multiple AccessKeys. We request you to delete one of them and reply us back with the same. Thank you.',
                            'Charset': 'utf-8'
                        }
                    }
                }   
            )
            print("Email sent successfully", res)
        except Exception as ex:
            print ("Email sending failed", ex)

for user_details in iam_users_list:
    username = user_details['UserName']
    res = iam_client.list_access_keys(UserName = username)
    for keyvalue in res['AccessKeyMetadata']:
        if keyvalue['Status'] == 'Active':    
            usertags = iam_client.list_user_tags(UserName = username)
            if usertags['Tags']:
                for tag in usertags['Tags']:
                    if tag['Key'] == 'Email':
                        create_users_list(tag, keyvalue, user_details)
                        emailIdArr.append(username)
                        
emailIdList = emailIdArr
for i in range(0, len(emailIdList)):    
    for j in range(i+1, len(emailIdList)):    
        if(emailIdList[i] == emailIdList[j]):    
            multipleKeysUser = emailIdList[j]
            if multipleKeysUser:
                email_multiple_keys_user(multipleKeysUser)
