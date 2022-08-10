import boto3, os, time, datetime, json, csv
from datetime import date
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')

db_client = boto3.client('dynamodb', region_name = 'ap-south-1')

db_resource = boto3.resource('dynamodb', region_name = 'ap-south-1')

db_table = db_resource.Table('Users-List-IAM')

response = db_table.scan()
data = response['Items']

def update_new_access_key(userData):
    userName = userData['userName']
    currentAccessKeyId = userData['currentAccessKey']
    newAccessKeyId = userData['newAccessKey']
    try:
        db_table.update_item(
            Key={'userName': userName},
            UpdateExpression='SET currentAccessKey = :newAccessKeyId, newAccessKey = :Null',
            ExpressionAttributeValues={':newAccessKeyId': newAccessKeyId , ':Null': 'Null'},
        )
        print('CurrentAccessKey replaced and NewAccessKey set to Null')
    except Exception as ex:
        print ("NewAccessKey updation Failed", ex)


for userData in data:
    if userData['newAccessKey'] != 'Null':
        delete_access_key = iam_client.delete_access_key(
            UserName = userData['userName'],
            AccessKeyId = userData['currentAccessKey']
        )
        print('Old access key deleted successfully')
        update_new_access_key(userData)
    else:
        print('User access key is still valid')

     
    

