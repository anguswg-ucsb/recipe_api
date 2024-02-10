#!/bin/bash

# AWS Account Number
AWS_ACCOUNT_NUMBER=$1

# S3 bucket and ECR repo names
BUCKET_NAME=$2
INVENTORY_BUCKET_NAME="${BUCKET_NAME}-inventory"  # New inventory bucket name

BACKUP_BUCKET_NAME=${3:-"${BUCKET_NAME}-backup"}

# ECR repo names 
ECR_REPO_NAME=$4

# AWS Region to create/check resources, if not given, use "us-west-1"
AWS_REGION=${5:-"us-west-1"}
LOCATION_CONSTRAINT=${AWS_REGION}

# AWS Profile, if not given, use "default"
AWS_PROFILE=${6:-"default"}

# # S3 bucket and ECR repo names
# BUCKET_NAME="recipes-output-bucket"
# ECR_REPO_NAME="extract-ingredients-lambda-repository" 

# # regions to create/check resources
# AWS_REGION="us-west-1"
# LOCATION_CONSTRAINT="us-west-1"
# AWS_PROFILE="default"

echo "- BUCKET_NAME: $BUCKET_NAME"
echo "- INVENTORY_BUCKET_NAME: $INVENTORY_BUCKET_NAME"
echo "- BACKUP_BUCKET_NAME: $BACKUP_BUCKET_NAME"
echo "- ECR_REPO_NAME: $ECR_REPO_NAME"
echo "- AWS_REGION: $AWS_REGION"
echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
echo "- AWS_PROFILE: $AWS_PROFILE"

# Export Output S3 Bucket Name, Output S3 inventory bucket and ECR Repository Name as Terraform variables
export TF_VAR_output_s3_bucket_name="$BUCKET_NAME"
export TF_VAR_output_s3_inventory_bucket_name="$INVENTORY_BUCKET_NAME"
export TF_VAR_backup_s3_bucket_name="$BACKUP_BUCKET_NAME"
export TF_VAR_lambda_ecr_repository_name="$ECR_REPO_NAME"

# export TF_VAR_output_s3_bucket_name="recipes-output-bucket"
# export TF_VAR_lambda_ecr_repository_name="extract-ingredients-lambda-repository"

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
#                "s3:x-amz-acl": "bucket-owner-full-control",
#                "aws:SourceArn": "arn:aws:s3:::'"${INVENTORY_BUCKET_NAME}"'"
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