#!/bin/bash

# Usage: sh/backup_db.sh db_name backup_bucket_name
echo "Backing up ${DB_NAME} database to S3..."
echo "- Backup S3 bucket: ${BACKUP_BUCKET_NAME}"

DIR=$(dirname "${BASH_SOURCE[0]}")

DB_NAME=${1:-"db_name"}

BACKUP_BUCKET_NAME=${2:-"backup_bucket_name"}

DUMP_FILE_NAME="$DB_NAME_$(date +"%Y_%m_%d_%H_%M")_backup.dump"

DATE_TIME=$(date +"%Y_%m_%d_%H_%M")

DUMP_PATH="$DIR/$DUMP_FILE_NAME"
# DUMP_PATH="$DIR/$DB_NAME_$(date +"%Y_%m_%d_%H_%M")_backup.dump"

echo "- DIR: $DIR"
echo "- DB_NAME: $DB_NAME"
echo "- BACKUP_BUCKET_NAME: $BACKUP_BUCKET_NAME"
echo "- DUMP_FILE_NAME: $DUMP_FILE_NAME"
echo "- DUMP_PATH: $DUMP_PATH"
echo "- DATE_TIME: $DATE_TIME"

echo "Dumping database backup to: /tmp/$DUMP_FILE_NAME"

# # DUMP the database
sudo -u postgres pg_dump --encoding utf8 --format c --compress 9 --file /tmp/$DUMP_FILE_NAME $DB_NAME
# sudo -u postgres pg_dump recipe_db > /tmp/tempfile
# # sudo -u postgres pg_dump --encoding utf8 --format c --compress 9 --file ./2024_02_03_15_50_backup.dump recipe_db

# sudo -u postgres pg_dump $DB_NAME > /tmp/$DUMP_PATH
# sudo -u postgres pg_dump --encoding utf8 --format c --compress 9 --file tmp/$DUMP_PATH $DB_NAME
# sudo -u postgres pg_dump --encoding utf8 --format c --compress 9 --file /tmp/$DUMP_PATH $DB_NAME
# pg_dump --encoding utf8 --format c --compress 9 --file $DUMP_PATH $DB_NAME
# pg_dump --encoding utf8 --format c --compress 9 --file ./2024_02_03_15_50_backup.dump recipe_db
# DUMP_KEY=$DUMP_PATH | cut -c 3- # Remove the ./ from the path

echo "Uploading the dump file to S3"

# # # Upload the dump file to S3
# aws s3 cp /tmp/$DUMP_FILE_NAME s3://$BACKUP_BUCKET_NAME/$DUMP_FILE_NAME
# # s3cmd put $DUMP_PATH s3://$DB_NAME-db-backups/$DB_NAME/$DUMP_KEY

echo "Removing the dump file from disk"

# # Remove the dump file from disk
rm /tmp/$DUMP_FILE_NAME