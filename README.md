# aws-key-rotation
To automate the AWS keys rotation.

The 'iam-users-list' script will fetch the list of iam users with access/secret keys and store that in aws DynamoDb. It also send email to users who has multiple access keys requesting to delete one of them.
The 'create-access-key' script will notify users to create new access/secret keys if the keys active days are b/w 80 & 90 days. It also create new keys automatically if the old keys are older than 90 days and send them via email to the user in a csv file.
The 'delete-access-key' script will delete the old keys if the users fails to create new one after a week of notification and replaces the new key with old one in the Dynamodb.
