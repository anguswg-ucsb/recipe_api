#!/bin/bash

# Description: This script sets up AWS-related configurations including S3 bucket names, ECR repository names, AWS regions, and profiles.
# It takes several arguments to customize the configurations. If some arguments are not provided, default values are used.

# Usage: ./script.sh <AWS_ACCOUNT_NUMBER> <BUCKET_NAME> <TF_STATE_S3_BUCKET_NAME> <ECR_REPO_NAME> <AWS_REGION> <AWS_PROFILE> <RUNNING_ON_GITHUB_ACTION>
# Arguments:
#   - AWS_ACCOUNT_NUMBER: The AWS account number.
#   - BUCKET_NAME: The name of the main S3 bucket.
#   - TF_STATE_S3_BUCKET_NAME: The name of the Terraform state S3 bucket.
#   - ECR_REPO_NAME: The name of the ECR repository.
#   - AWS_REGION: The AWS region to create/check resources. Default is "us-west-1".
#   - AWS_PROFILE: The AWS profile to use. Default is "default".
#   - RUNNING_ON_GITHUB_ACTION: Flag to determine whether to export variables to $GITHUB_ENV. Default is "false".

# Example usage:
# ./build_static_resources.sh 123456789012 my-bucket-name my-backup-bucket my-tf-state-bucket my-ecr-repo-name us-west-2 my-aws-profile false

# Example usage:
# ./build_static_resources.sh 123456789012 my-bucket-name my-backup-bucket my-tf-state-bucket my-ecr-repo-name us-west-2 my-aws-profile true

# AWS Account Number
AWS_ACCOUNT_NUMBER=$1

# S3 bucket and ECR repo names
BUCKET_NAME=$2
INVENTORY_BUCKET_NAME="${BUCKET_NAME}-inventory"  # New inventory bucket name
REPLICA_BUCKET_NAME="${BUCKET_NAME}-replica"  # New bucket name in another region

BACKUP_BUCKET_NAME=${3:-"${BUCKET_NAME}-backup"}

# Terraform state S3 bucket name
TF_STATE_S3_BUCKET_NAME=$4

# ECR repo names 
ECR_REPO_NAME=$5

# AWS Region to create/check resources, if not given, use "us-west-1"
AWS_REGION=${6:-"us-west-1"}
LOCATION_CONSTRAINT=${AWS_REGION}

REPLICA_AWS_REGION=${7:-"us-west-2"}
REPLICA_LOCATION_CONSTRAINT=${REPLICA_AWS_REGION}

# AWS Profile, if not given, use "default"
AWS_PROFILE=${8:-"default"}

# Flag to determine whether to export variables to $GITHUB_ENV
RUNNING_ON_GITHUB_ACTION=${9:-"false"}

echo "- BUCKET_NAME: $BUCKET_NAME"
echo "- INVENTORY_BUCKET_NAME: $INVENTORY_BUCKET_NAME"
echo "- REPLICA_BUCKET_NAME: $REPLICA_BUCKET_NAME"
echo "- BACKUP_BUCKET_NAME: $BACKUP_BUCKET_NAME"
echo "- TF_STATE_S3_BUCKET_NAME: $TF_STATE_S3_BUCKET_NAME"
echo "- ECR_REPO_NAME: $ECR_REPO_NAME"
echo "- AWS_REGION: $AWS_REGION"
echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
echo "- REPLICA_AWS_REGION: $REPLICA_AWS_REGION"
echo "- REPLICA_LOCATION_CONSTRAINT: $REPLICA_LOCATION_CONSTRAINT"
echo "- AWS_PROFILE: $AWS_PROFILE"

# -----------------------------------------------------------------------------------------------
# ----- Create S3 bucket for outputs (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if the output bucket ALREADY EXISTS
if ! aws s3api head-bucket --bucket "$BUCKET_NAME" --profile "$AWS_PROFILE" 2>/dev/null; then
    echo "--> Creating $BUCKET_NAME bucket"

    # Create the output bucket if it DOESN'T exist
    aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --create-bucket-configuration LocationConstraint="$LOCATION_CONSTRAINT"

    # Enable versioning on the bucket
    aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --region "$AWS_REGION"  --profile "$AWS_PROFILE" --versioning-configuration Status=Enabled

    echo "Versioning enabled on S3 bucket $BUCKET_NAME."

else
    echo "Bucket $BUCKET_NAME already exists."
fi
# -----------------------------------------------------------------------------------------------
# ----- Create S3 bucket for REPLICATION of outputs (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if the another bucket in another region ALREADY EXISTS
if ! aws s3api head-bucket --bucket "$REPLICA_BUCKET_NAME" --profile "$AWS_PROFILE" --region "$REPLICA_AWS_REGION" 2>/dev/null; then
    echo "--> Creating $REPLICA_BUCKET_NAME bucket in $REPLICA_AWS_REGION"

    # Create the output bucket if it DOESN'T exist
    aws s3api create-bucket --bucket "$REPLICA_BUCKET_NAME" --region "$REPLICA_AWS_REGION" --profile "$AWS_PROFILE" --create-bucket-configuration LocationConstraint="$REPLICA_LOCATION_CONSTRAINT"

    # Enable versioning on the bucket
    aws s3api put-bucket-versioning --bucket "$REPLICA_BUCKET_NAME" --region "$REPLICA_AWS_REGION"  --profile "$AWS_PROFILE" --versioning-configuration Status=Enabled

    echo "Versioning enabled on S3 bucket $REPLICA_BUCKET_NAME."

    # # Enable replication for the second bucket
    aws s3api put-bucket-replication --bucket "$BUCKET_NAME" --replication-configuration "{
        \"Role\": \"arn:aws:iam::${AWS_ACCOUNT_NUMBER}:role/service-role/AmazonS3ReplicationRole\",
        \"Rules\": [
            {
                \"Status\": \"Enabled\",
                \"Priority\": 1,
                \"Destination\": {
                    \"Bucket\": \"arn:aws:s3:::${REPLICA_BUCKET_NAME}\",
                    \"Account\": \"${AWS_ACCOUNT_NUMBER}\",
                    \"StorageClass\": \"STANDARD\",
                    \"AccessControlTranslation\": {
                        \"Owner\": \"Destination\"
                    }
                },
                \"DeleteMarkerReplication\": {
                    \"Status\": \"Enabled\"
                },
                \"Filter\": {
                    \"Prefix\": \"\"
                }
            }
        ]
    }"

    # echo "Replication enabled for S3 bucket $BUCKET_NAME to replicate to $REPLICA_BUCKET_NAME."

else
    echo "Bucket $REPLICA_BUCKET_NAME already exists in $REPLICA_AWS_REGION."
fi
# -----------------------------------------------------------------------------------------------
# ----- Create S3 bucket INVENTORY of output bucket (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# Check if the inventory bucket ALREADY EXISTS
if ! aws s3api head-bucket --bucket "$INVENTORY_BUCKET_NAME" --profile "$AWS_PROFILE" 2>/dev/null; then
    echo "--> Creating $INVENTORY_BUCKET_NAME bucket"

    # Create the inventory bucket if it DOESN'T exist
    aws s3api create-bucket --bucket "$INVENTORY_BUCKET_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --create-bucket-configuration LocationConstraint="$LOCATION_CONSTRAINT"
else
    echo "Bucket $INVENTORY_BUCKET_NAME already exists."
fi

# Check if the output bucket ALREADY HAS an inventory configuration
if aws s3api get-bucket-inventory-configuration --bucket "$BUCKET_NAME" --profile "$AWS_PROFILE" --id RecipesOutputDailyInventory 2>/dev/null; then
    echo "Bucket $BUCKET_NAME already has an inventory configuration."
else
    echo "--> Creating inventory configuration for bucket $BUCKET_NAME with destination bucket $INVENTORY_BUCKET_NAME."
    # Set up daily inventory for the output bucket with the inventory bucket as the destination
    aws s3api put-bucket-inventory-configuration \
        --bucket "$BUCKET_NAME" \
        --id RecipesOutputDailyInventory \
        --profile "$AWS_PROFILE" \
        --inventory-configuration '{
            "Id": "RecipesOutputDailyInventory",
            "Destination": {
                "S3BucketDestination": {
                    "AccountId": "'"$AWS_ACCOUNT_NUMBER"'",
                    "Bucket": "arn:aws:s3:::'"$INVENTORY_BUCKET_NAME"'",
                    "Format": "CSV",
                    "Prefix": "daily-inventory",
                    "Encryption": {
                        "SSES3": {}
                    }
                }
            },
            "IsEnabled": true,
            "IncludedObjectVersions": "Current",
            "Schedule": {
                "Frequency": "Daily"
            }
        }'

fi

# -----------------------------------------------------------------------------------------------
# ----- Apply bucket policy for the INVENTORY bucket -----
# -----------------------------------------------------------------------------------------------
INVENTORY_BUCKET_POLICY_ID="${INVENTORY_BUCKET_NAME}-bucket-policy"

echo "Creating bucket policy for $INVENTORY_BUCKET_NAME with ID: $INVENTORY_BUCKET_POLICY_ID"

# Apply bucket policy
aws s3api put-bucket-policy --bucket "$INVENTORY_BUCKET_NAME" --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "'"$INVENTORY_BUCKET_POLICY_ID"'",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": [
        "arn:aws:s3:::'"$INVENTORY_BUCKET_NAME"'",
        "arn:aws:s3:::'"$INVENTORY_BUCKET_NAME"'/*"
      ],
      "Condition": {
        "StringEquals": {
            "s3:x-amz-acl": "bucket-owner-full-control",
            "aws:SourceAccount": "'"$AWS_ACCOUNT_NUMBER"'"
        },
        "ArnLike": {
            "aws:SourceArn": "arn:aws:s3:::'"${BUCKET_NAME}"'"
        }
      }
    }
  ]
}'
# # # Policy JSON string
# POLICY='{
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "AllowInventoryReports",
#             "Effect": "Allow",
#             "Action": "s3:PutObject",
#             "Resource": "arn:aws:s3:::'"${INVENTORY_BUCKET_NAME}"'/*",
#             "Condition": {
#                 "StringEquals": {
#                     "s3:x-amz-acl": "bucket-owner-full-control"
#                 },
#                 "StringLike": {
#                     "aws:SourceArn": "arn:aws:s3:::'"${INVENTORY_BUCKET_NAME}"'"
#                 }
#             }
#         }
#     ]
# }'

# # Policy JSON string
# S3_BUCKET_POLICY='{
#     "Version": "2012-10-17",
#     "Statement": [
#       {
#          "Effect": "Allow",
#          "Principal": {
#             "Service": "s3.amazonaws.com"
#          },
#          "Action": "s3:PutObject",
#          "Resource": [
#             "arn:aws:s3:::'"${INVENTORY_BUCKET_NAME}"'",
#             "arn:aws:s3:::'"${INVENTORY_BUCKET_NAME}"'/*"
#          ],
#          "Condition": {
#             "StringEquals": {
            #    "s3:x-amz-acl": "bucket-owner-full-control",
            #    "aws:SourceArn": "arn:aws:s3:::'"${INVENTORY_BUCKET_NAME}"'"
#             },
#             "ArnLike": {
#                 "aws:SourceArn": "arn:aws:s3:::'"${BUCKET_NAME}"'"
#             }
#          }
#       }
#    ]
# }'

# # Create IAM policy
# POLICY_ARN=$(aws iam create-policy \
#     --policy-name InventoryBucketPolicy \
#     --policy-document "$POLICY" \
#     --profile "$AWS_PROFILE" \
#     --query 'Policy.Arn' \
#     --output text
# )

# echo "IAM policy created with ARN: $POLICY_ARN"

# # Attach policy to the inventory bucket
# aws s3api put-bucket-policy \
#     --bucket "$INVENTORY_BUCKET_NAME" \
#     --policy "$S3_BUCKET_POLICY" \
#     --profile "$AWS_PROFILE"

# -----------------------------------------------------------------------------------------------
# ----- Create S3 bucket for Database backups (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if the DB backup bucket ALREADY EXISTS
if ! aws s3api head-bucket --bucket "$BACKUP_BUCKET_NAME" --profile "$AWS_PROFILE" 2>/dev/null; then
    echo "--> Creating $BACKUP_BUCKET_NAME bucket"

    # Create the output bucket if it DOESN'T exist
    aws s3api create-bucket --bucket "$BACKUP_BUCKET_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --create-bucket-configuration LocationConstraint="$LOCATION_CONSTRAINT"

    # Enable versioning on the bucket
    aws s3api put-bucket-versioning --bucket "$BACKUP_BUCKET_NAME" --region "$AWS_REGION"  --profile "$AWS_PROFILE" --versioning-configuration Status=Enabled

    echo "Versioning enabled on S3 bucket $BACKUP_BUCKET_NAME."

else
    echo "Bucket $BACKUP_BUCKET_NAME already exists."
fi

# -----------------------------------------------------------------------------------------------
# ----- Create S3 bucket to keep Terraform state files (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if Terraform state S3 bucket ALREADY EXISTS
if ! aws s3api head-bucket --bucket "$TF_STATE_S3_BUCKET_NAME" 2>/dev/null; then
    # Create the Terraform state S3 bucket if it DOESN'T exist
    aws s3api create-bucket --bucket "$TF_STATE_S3_BUCKET_NAME" --region "$AWS_REGION" --create-bucket-configuration LocationConstraint="$LOCATION_CONSTRAINT"
    
    echo "S3 bucket $TF_STATE_S3_BUCKET_NAME created."

    # Enable versioning on the bucket
    aws s3api put-bucket-versioning --bucket "$TF_STATE_S3_BUCKET_NAME" --region "$AWS_REGION" --versioning-configuration Status=Enabled

    echo "Versioning enabled on S3 bucket $TF_STATE_S3_BUCKET_NAME."

else
    echo "Bucket $TF_STATE_S3_BUCKET_NAME already exists."
fi

# -----------------------------------------------------------------------------------------------
# ----- Create the ECR Repo (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if the ECR repository ALREADY EXISTS
if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" 2>/dev/null; then
    # create the ECR repository if it DOESN'T exist
    aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION"
    echo "ECR repository $ECR_REPO_NAME created."
else
    echo "ECR repository $ECR_REPO_NAME already exists."
fi

# Get the ECR Repositories URL and export it as a variable for Terraform (TF_VAR_lambda_ecr_repository_url)
ECR_REPO_URL=$(aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --query 'repositories[0].repositoryUri' --output text)
export TF_VAR_lambda_ecr_repository_url="$ECR_REPO_URL"

echo "ECR repository URL: $ECR_REPO_URL"

# -----------------------------------------------------------------------------------------------
# ----- Export Terraform variables -----
# -----------------------------------------------------------------------------------------------

# Export S3 bucket names and ECR repo name/URL as Terraform variables
export TF_VAR_output_s3_bucket_name="$BUCKET_NAME" # output bucket name
export TF_VAR_replica_s3_bucket_name="$REPLICA_BUCKET_NAME" # replica bucket name
export TF_VAR_output_s3_inventory_bucket_name="$INVENTORY_BUCKET_NAME" # inventory bucket name
export TF_VAR_backup_s3_bucket_name="$BACKUP_BUCKET_NAME" # backup bucket name
export TF_VAR_tf_state_s3_bucket_name="$TF_STATE_S3_BUCKET_NAME" # Terraform state S3 bucket name
export TF_VAR_lambda_ecr_repository_name="$ECR_REPO_NAME" # ECR repository name
export TF_VAR_lambda_ecr_repository_url="$ECR_REPO_URL"

# Check if the script is running on GitHub Actions and the flag is set to true
if [[ "$RUNNING_ON_GITHUB_ACTION" == "true" ]]; then
    echo "Running on GitHub Actions, exporting environment variables to Github Env..."
    # Export the environment variables to $GITHUB_ENV
    echo "TF_VAR_output_s3_bucket_name=$BUCKET_NAME" >> $GITHUB_ENV
    echo "TF_VAR_replica_s3_bucket_name=$REPLICA_BUCKET_NAME" >> $GITHUB_ENV
    echo "TF_VAR_output_s3_inventory_bucket_name=$INVENTORY_BUCKET_NAME" >> $GITHUB_ENV
    echo "TF_VAR_backup_s3_bucket_name=$BACKUP_BUCKET_NAME" >> $GITHUB_ENV
    echo "TF_VAR_tfstate_s3_bucket_name=$TF_STATE_S3_BUCKET_NAME" >> $GITHUB_ENV
    echo "TF_VAR_lambda_ecr_repository_name=$ECR_REPO_NAME" >> $GITHUB_ENV
    echo "TF_VAR_lambda_ecr_repository_url=$ECR_REPO_URL" >> $GITHUB_ENV
    echo "Exported TF_VAR_output_s3_bucket_name, TF_VAR_replica_s3_bucket_name, TF_VAR_output_s3_inventory_bucket_name, TF_VAR_backup_s3_bucket_name, TF_VAR_tfstate_s3_bucket_name, and TF_VAR_lambda_ecr_repository_name to Github Env"
fi


# # check if the ECR repository ALREADY EXISTS
# if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" 2>/dev/null; then
#     # create the ECR repository if it DOESN'T exist
#     aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION"
#     echo "ECR repository $ECR_REPO_NAME created."
# else
#     echo "ECR repository $ECR_REPO_NAME already exists."
# fi

# # Get the ECR Repositories URL and export it as a variable for Terraform (TF_VAR_lambda_ecr_repository_url)
# ECR_REPO_URL=$(aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --query 'repositories[0].repositoryUri' --output text)
# export TF_VAR_lambda_ecr_repository_url="$ECR_REPO_URL"

# echo "ECR repository URL: $ECR_REPO_URL"

# # AWS CLI and Docker commands to login, build, tag, and push Docker image
# aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin $AWS_ACCOUNT_NUMBER.dkr.ecr.$AWS_REGION.amazonaws.com

# # build Docker image
# docker build -t extract-ingredients-lambda-repository lambda_containers/extract_ingredients_lambda/

# # tag Docker image
# docker tag extract-ingredients-lambda-repository:latest "$AWS_ACCOUNT_NUMBER.dkr.ecr.$AWS_REGION.amazonaws.com/extract-ingredients-lambda-repository:latest"

# # push Docker image to ECR repository
# docker push "$AWS_ACCOUNT_NUMBER.dkr.ecr.$AWS_REGION.amazonaws.com/extract-ingredients-lambda-repository:latest"