#!/bin/bash

# When the EC2 instance reboots, restart the SQS Consumer script to continue processing messages from the queue
# Usage: sh/on_reboot.sh DB_NAME DB_USERNAME DB_PASSWORD S3_DOWNLOADS_PATH SQS_QUEUE_URL AWS_REGION

# get DB_NAME, DB_USERNAME, DB_PASSWORD, S3_DOWNLOADS_PATH, SQS_QUEUE_URL, AWS_REGION
DB_NAME=${1:-"db_name"}
DB_USERNAME=${2:-"username"}
DB_PASSWORD=${3:-"password"}
S3_DOWNLOADS_PATH=${4:-"/usr/local/s3_downloads"}
SQS_QUEUE_URL=${5:-"https://sqs.us-west-1.amazonaws.com/123456789012/MyQueue"}
AWS_REGION=${6:-"us-west-1"}

# Run the Python script (SQS Consumer)
DB_NAME=$DB_NAME \
DB_USERNAME=$DB_USERNAME \
DB_PASSWORD=$DB_PASSWORD \
S3_DOWNLOADS_PATH=$S3_DOWNLOADS_PATH \
SQS_QUEUE_URL=$SQS_QUEUE_URL \
AWS_REGION=$AWS_REGION \
python3 /usr/local/sqs_consumer/main.py

# # Get secrets values from AWS Secrets Manager
# SECRETS_MANAGER_SECRET_ID=${1:-"default-secret-id"}
# SECRET_KEY=${2:-"default_secret_key"}

# echo "Getting secret value from AWS Secrets Manager..."

# # Retrieve the secret value and store it in a variable
# SECRET_VALUE=$(aws secretsmanager get-secret-value --secret-id $SECRETS_MANAGER_SECRET_ID --query SecretString --output text | grep -o "\"$SECRET_KEY\":\"[^\"]*" |  grep -o '[^"]*$')

# # Check if the secret value is not empty
# if [ -n "$SECRET_VALUE" ]; then
#     echo "Secret value retrieved successfully."
# else
#     echo "Failed to retrieve secret value."
# fi