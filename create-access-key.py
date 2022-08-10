import boto3, os, time, datetime, json, csv
from datetime import date
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

iam_client = boto3.client('iam')

db_client = boto3.client('dynamodb', region_name = 'ap-south-1')

db_resource = boto3.resource('dynamodb', region_name = 'ap-south-1')

db_table = db_resource.Table('Users-List-IAM')

ses_client = boto3.client('ses', region_name='ap-south-1')

response = db_table.scan()
data = response['Items']
print(response)

def email_users(emailId, activeDays):
    if 80 < activeDays <= 90:
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
                        'Data': 'AccessKey Rotation Notification',
                        'Charset': 'utf-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': 'Your AccessKeyId is active for more than 80 days, please create a new access key and  delete the old one',
                            'Charset': 'utf-8'
                        }
                    }
                }   
            )
            print("Email sent successfully", res)
        except Exception as ex:
            print ("Email sending failed", ex)
    if activeDays > 90:
        try:
            message = MIMEMultipart()
            message['Subject'] = 'New AccessKey Creation Notification'
            sender = 'security@clouddestinations.com'
            receiver = emailId
            email_body = MIMEText('Your AccessKeyId is active for more than 90 days. We have created a new AccessKeyId and attached the credentials file in this email. Please use the new Key and delete the old one.', 'html')
            message.attach(email_body)
            
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(open('aws_access_key.csv', "rb").read())
            attachment = MIMEApplication(open('aws_access_key.csv', 'rb').read())
            attachment.add_header('Content-Disposition', 'attachment', filename = 'aws_access_key.csv')
            message.attach(attachment)
                
            response = ses_client.send_raw_email(
                Source = sender,
                Destinations = [receiver],
                RawMessage = {
                    'Data': message.as_string()
                } 
            )
            print("Email sent successfully")
        except Exception as ex:
            print ("Email sending failed", ex) 


def update_users_list(userData, newAccessKeyId, activeDays):  
    userName = userData['userName']
    emailId = userData['emailId']
    try:
        response = db_table.update_item(
            Key={
                'userName': userName
            },
            UpdateExpression='SET newAccessKey = :newAccessKeyId',
            ExpressionAttributeValues={
                ':newAccessKeyId': newAccessKeyId
            },
        )
        print('NewAccessKey updated successfully')
        email_users(emailId, activeDays)
    except Exception as ex:
        print ("NewAccessKey updation Failed", ex)
        
 
def access_key_creation(userData, emailId, activeDays):
    try:
        create_access_key = iam_client.create_access_key(
            UserName = userData['userName']
        )
        access_key_data = create_access_key['AccessKey']
        userName = access_key_data['UserName']
        accessKeyId = access_key_data['AccessKeyId']
        secretAccessKey = access_key_data['SecretAccessKey']
        
        # last_used = iam_client.get_access_key_last_used(
        # AccessKeyId = access_key_data['AccessKeyId']
        # )
        # print(last_used)
        # key_last_used = last_used['AccessKeyLastUsed']
        # access_key_last_used = key_last_used['LastUsedDate']
        # print(access_key_last_used)
            
        file = open('aws_access_key.csv', 'w', newline='')
        writer = csv.writer(file)
        writer.writerow(['UserName', 'AccessKeyId', 'SecretAccessKey'])
        writer.writerow([userName, accessKeyId, secretAccessKey])
        print('AccessKey Created Successfully')
        file.close()
        update_users_list(userData, accessKeyId, activeDays)
        # if access_key_last_used == Null:
            # print(True)
        # else:
            # print(False)
    except Exception as ex:
        print ("AccessKey Creation Failed", ex)
        
        
for userData in data:
    activeDays = userData['keyActiveDays']
    emailId = userData['emailId']
    if activeDays > 80:
        access_key_creation(userData, emailId, activeDays)
    else:
        print('No access keys has been expired')
        
