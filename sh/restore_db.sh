#!/bin/bash

DB_NAME=${1:-"db_name"}
BACKUP_BUCKET_NAME=${2:-"backup_bucket_name"}
AWS_REGION=${3:-"us-west-1"}
# AWS_PROFILE=${4:-"default"}

# Get current year and month
YEAR=$(date -d "$(date +%Y-%m-1) 0 month" +%Y)
MONTH=$(date -d "$(date +%Y-%m-1) 0 month" +%m)

# Get last year and month
LAST_YEAR=$(date -d "$(date +%Y-%m-1) -1 month" +%Y)
LAST_MONTH=$(date -d "$(date +%Y-%m-1) -1 month" +%m)

# # Get current year and month
# YEAR=${5:-$(date +%Y)}
# MONTH=${6:-$(date +%m)}
# # Calculate the previous month and year
# LAST_MONTH=$(date -v -1m +%m)
# LAST_YEAR=$(date -v -1m +%Y)

# # Adjust for January (previous month becomes December of previous year)
# if [ "$MONTH" -eq "01" ]; then
#   LAST_MONTH="12"
#   LAST_YEAR=$((YEAR - 1))
# fi

echo "AWS_REGION: $AWS_REGION"
echo "Current year: $YEAR"
echo "Current month: $MONTH"

echo "Last year: $LAST_YEAR"
echo "Last month: $LAST_MONTH"

# Specify the S3 object keys for current and previous months
CURRENT_OBJECT_KEY="${YEAR}/${MONTH}/${DB_NAME}_backup.dump"
PREVIOUS_OBJECT_KEY="${LAST_YEAR}/${LAST_MONTH}/${DB_NAME}_backup.dump"

# # Check if the backup S3 bucket exists
# if aws s3 ls s3://recipes-db-backup-bucket &> /dev/null; then

echo "CURRENT_OBJECT_KEY: $CURRENT_OBJECT_KEY"
echo "PREVIOUS_OBJECT_KEY: $PREVIOUS_OBJECT_KEY"
echo "Checking if the backup S3 bucket exists..."

# check if the output bucket ALREADY EXISTS
if aws s3api head-bucket --bucket "$BACKUP_BUCKET_NAME" 2>/dev/null; then
# if aws s3api head-bucket --bucket "$BACKUP_BUCKET_NAME" --profile "$AWS_PROFILE" 2>/dev/null; then
    echo "Backup S3 bucket EXISTS."

    # Check if CURRENT_OBJECT_KEY is in the S3 bucket
    echo "Checking if backup dump files for current or previous month exists in S3 bucket $BACKUP_BUCKET_NAME..."
    echo "- Current month backup: $CURRENT_OBJECT_KEY"
    echo "- Previous month backup: $PREVIOUS_OBJECT_KEY"

    if aws s3api head-object --bucket "$BACKUP_BUCKET_NAME" --key "$CURRENT_OBJECT_KEY" --region "$AWS_REGION" 2>/dev/null; then 
        echo "Current month backup file EXISTS in S3 bucket $BUCKET_NAME."
        echo "Downloading the CURRENT months backup file from S3 bucket..."
        
        # Define the S3 URI and dump file path
        S3_OBJECT_URI="s3://${BACKUP_BUCKET_NAME}/${CURRENT_OBJECT_KEY}" 
        DUMP_FILE="${DB_NAME}_backup.dump"
        # DUMP_FILE="${DB_NAME}_${YEAR}_${MONTH}_backup.dump"

        echo "S3_OBJECT_URI: $S3_OBJECT_URI"
        echo "DUMP_FILE: $DUMP_FILE"

        aws s3 cp ${S3_OBJECT_URI} ${DUMP_FILE}

        # Restore the database from the dump file
        sudo -u postgres pg_restore -v -C -d postgres ${DUMP_FILE}
        # sudo -u postgres pg_restore -v -h localhost -p 5432 -d ${DB_NAME} ${DUMP_FILE}
        # sudo -u postgres pg_restore -C --dbname=${DB_NAME} ${DUMP_FILE}
        # pg_restore --dbname=${DB_NAME} ${DUMP_FILE}

        echo "Database ${DB_NAME} restored successfully from ${DUMP_FILE}."

        echo "Removing the dump file from the system..."

        #  Remove the dump file
        rm ${DUMP_FILE}

        # Database restored successfully
        echo "Restoration complete"
        # Upload an empty CSV file
        # aws s3 cp "$LOCAL_CSV_PATH" s3://"$BUCKET_NAME"/"$S3_OBJECT_KEY" --region "$AWS_REGION" 
        # echo "$CSV_CONTENT" | aws s3 cp - s3://"$BUCKET_NAME"/"$S3_OBJECT_KEY" --region "$AWS_REGION" 
        
        # echo "- Empty CSV file uploaded to S3: $BUCKET_NAME/$S3_OBJECT_KEY"
    elif aws s3api head-object --bucket "$BACKUP_BUCKET_NAME" --key "$PREVIOUS_OBJECT_KEY" --region "$AWS_REGION" 2>/dev/null; then 
        echo "Previous month backup file EXISTS in S3 bucket $BUCKET_NAME."
        echo "Downloading the PREVIOUS months backup file from S3 bucket..."
        
        # Define the S3 URI and dump file path
        S3_OBJECT_URI="s3://${BACKUP_BUCKET_NAME}/${PREVIOUS_OBJECT_KEY}" 
        DUMP_FILE="${DB_NAME}_backup.dump"
        # DUMP_FILE="${DB_NAME}_${YEAR}_${MONTH}_backup.dump"

        echo "S3_OBJECT_URI: $S3_OBJECT_URI"
        echo "DUMP_FILE: $DUMP_FILE"

        aws s3 cp ${S3_OBJECT_URI} ${DUMP_FILE}

        # Restore the database from the dump file
        sudo -u postgres pg_restore -v -C -d postgres ${DUMP_FILE}
        # sudo -u postgres pg_restore -v -h localhost -p 5432 -d ${DB_NAME} ${DUMP_FILE}
        # sudo -u postgres pg_restore -C --dbname=${DB_NAME} ${DUMP_FILE}    
        # pg_restore --dbname=${DB_NAME} ${DUMP_FILE}

        echo "Database ${DB_NAME} restored successfully from ${DUMP_FILE}."
        echo "Removing the dump file from the system..."

        #  Remove the dump file
        rm ${DUMP_FILE}
                
        echo "Restoration complete"

    else
        echo "No suitable backup found in S3 bucket."
    fi

else
  echo "Backup S3 bucket DOES NOT EXIST."
fi


# # # Check if required arguments are provided
# # if [ $# -ne 3 ]; then
# #   echo "Usage: $0 <bucket_name> <object_key> <db_name>"
# #   exit 1
# # fi

# # Assign command line args to variables
# BACKUP_BUCKET_NAME=${1:-"backup_bucket_name"}
# OBJECT_KEY=${2:-"backup.dump"}
# DB_NAME=${3:-"db_name"}

# # Set the dump file name
# DUMP_FILE=${4:-"db_backup.dump"}

# S3_OBJECT_URI="s3://${BACKUP_BUCKET_NAME}/${OBJECT_KEY}"

# # Download the dump file from S3 bucket
# echo "Downloading the dump file from S3 bucket..."

# aws s3 cp ${S3_OBJECT_URI} ${DUMP_FILE}

# # aws s3 cp s3://${BACKUP_BUCKET_NAME}/${OBJECT_KEY} ${DUMP_FILE}

# # # Check if the download was successful
# # if [ $? -ne 0 ]; then
# #   echo "Failed to download the dump file from S3 bucket."
# #   exit 1
# # fi

# # Restore the database from the dump file
# sudo -u postgres pg_restore --dbname=${DB_NAME} ${DUMP_FILE}
# # pg_restore --dbname=${DB_NAME} ${DUMP_FILE}

# # # # # DUMP the database
# # cd /usr/local/ && sudo -u postgres pg_dump --encoding utf8 --format c --compress 9 --file $DUMP_PATH $DB_NAME

# # # Check if the restore was successful
# # if [ $? -ne 0 ]; then
# #   echo "Failed to restore the database from the dump file."
# #   exit 1
# # fi

# echo "Database ${DB_NAME} restored successfully from ${DUMP_FILE}."

# echo "Removing the dump file from the system..."

# #  Remove the dump file
# rm ${DUMP_FILE}
