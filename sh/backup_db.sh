#!/bin/bash

# Usage: sh/backup_db.sh db_name output_dir_path backup_bucket_name

# Declare variables
DIR=$(dirname "${BASH_SOURCE[0]}")

# Database name to generate a backup file for
DB_NAME=${1:-"db_name"}

# The directory to temporarily save the backup file to
OUTPUT_DIR=${2:-"/usr/local/tmp"}

# Name of the backup bucket to write the backup to
BACKUP_BUCKET_NAME=${3:-"backup_bucket_name"}

# Generate a filename for the DB dump backup based on current datetime 
DUMP_FILE_NAME="$DB_NAME"_"backup.dump"
# DUMP_FILE_NAME="$DB_NAME"_"$(date +"%Y_%m_%d_%H_%M")_backup.dump"

# Temporary path for the dump file (probably delete this line later)
DUMP_PATH="$OUTPUT_DIR/$DUMP_FILE_NAME"
# DUMP_PATH="$DIR/$DB_NAME_$(date +"%Y_%m_%d_%H_%M")_backup.dump"

# Current datetime for logging
DATE_TIME=$(date +"%Y_%m_%d_%H_%M")

# Get the year and month for the backup to use as a prefix for the S3 path
YEAR=$(date +"%Y")
MONTH=$(date +"%m")

# Create the S3 object URI
S3_OBJECT_URI="s3://$BACKUP_BUCKET_NAME/$YEAR/$MONTH/$DUMP_FILE_NAME"


echo "============================================" 
echo "Backing up ${DB_NAME} database to S3..."

echo "System details at time of backup: "
echo "- DATE_TIME: $DATE_TIME"
echo "- YEAR: $YEAR"
echo "- MONTH: $MONTH"

echo "Backup details: "
echo "- DIR: $DIR"
echo "- DB_NAME: $DB_NAME"
echo "- OUTPUT_DIR: $OUTPUT_DIR"
echo "- DUMP_FILE_NAME: $DUMP_FILE_NAME"
echo "- DUMP_PATH: $DUMP_PATH"

echo "S3 details: "
echo -e "- Backup S3 bucket (BACKUP_BUCKET_NAME): \n > $BACKUP_BUCKET_NAME"
echo -e "- S3 Object URI (S3_OBJECT_URI): \n > $S3_OBJECT_URI"
echo "============================================" 

echo "-> Dumping database backup to: $DUMP_PATH"

# # # DUMP the database
cd /usr/local/ && sudo -u postgres pg_dump --encoding utf8 -C --format c --compress 9 --file $DUMP_PATH $DB_NAME

echo "Uploading dump file to S3..."
echo -e "(DUMP_PATH) '$DUMP_PATH' --> \n\t --> (S3_OBJECT_URI) '$S3_OBJECT_URI'"
# logger -s -t "backup_db.sh" "Uploading the dump file to S3"

# # # Upload the dump file to S3
aws s3 cp $DUMP_PATH $S3_OBJECT_URI
# aws s3 cp /tmp/$DUMP_FILE_NAME s3://$BACKUP_BUCKET_NAME/$DUMP_FILE_NAME
# s3cmd put $DUMP_PATH s3://$DB_NAME-db-backups/$DB_NAME/$DUMP_KEY

echo "---> Removing the dump file from disk"
# logger -s -t "backup_db.sh" "Removing the dump file from disk"

# # Remove the dump file from disk
rm $DUMP_PATH
# rm /tmp/$DUMP_FILE_NAME

echo "'$DUMP_PATH' removed from disk"