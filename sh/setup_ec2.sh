#!/bin/bash

# print echo statement for debugging
echo "The value of S3_BUCKET is: ${S3_BUCKET}"
echo "The value of DB_NAME is: ${DB_NAME}"

# Variables for SQS Consumer to use
echo "The value of SCRIPTS_S3_BUCKET is: ${SCRIPTS_S3_BUCKET}"
echo "The value of SQS Consumer python script is: ${SQS_CONSUMER_PYTHON_SCRIPT}"
echo "The SQS_QUEUE_URL is: ${SQS_QUEUE_URL}"

echo "The value of BACKUP_BUCKET is: ${BACKUP_BUCKET}"
echo "The value of BACKUP_DB_SCRIPT is: ${BACKUP_DB_SCRIPT}"

# update 
sudo apt-get update -y && sudo apt-get upgrade -y

#  download AWS CLI
sudo apt-get install awscli -y

# Install Python and pip
sudo apt-get install python3 -y
sudo apt-get install python3-pip -y

echo "Installing pandas..."

# Install pandas
sudo pip3 install pandas

echo "Installing boto3..."

# Install boto3
sudo pip3 install boto3

# Download postgres and postgres-contrib
sudo apt-get install postgresql postgresql-contrib -y

# Alter the password for the postgres user
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${DB_PASSWORD}';"

# make changes to pg_hba.conf file
sudo sed -i '/# Database administrative login by Unix domain socket/!b;n;c\local   all             postgres                                trust' /etc/postgresql/14/main/pg_hba.conf
# sudo sed -i '/# Database administrative login by Unix domain socket/!b;n;c\local   all             postgres                                md5' /etc/postgresql/14/main/pg_hba.conf

sudo sh -c "echo 'host    all             all             0.0.0.0/0               trust' >> /etc/postgresql/14/main/pg_hba.conf"
# sudo sh -c "echo 'host    all             all             0.0.0.0/0               md5' >> /etc/postgresql/14/main/pg_hba.conf"
# sudo sh -c "echo 'host all all 0.0.0.0/0 md5' >> /etc/postgresql/14/main/pg_hba.conf"

sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/14/main/postgresql.conf

# sudo service postgresql restart
sudo systemctl restart postgresql

# Create a custom directory in /usr/local
sudo mkdir /usr/local/s3_downloads

# # Create the directory if it doesn't exist
# sudo mkdir /usr/local/s3_downloads

# Run chmod 755 on the directory to grant appropriate permissions
sudo chmod -R 755 /usr/local/s3_downloads
# sudo chmod +x /usr/local/s3_downloads

echo "Making usr/local/tmp directory for temporary backup files..."

# Create a custom directory in /usr/local
sudo mkdir /usr/local/tmp

# grant appropriate permissions to usr/local/tmp directory to write temporary backup files
sudo chmod -R a+rwx /usr/local/tmp
# sudo chmod -R 755 /usr/local/tmp

echo "Making shell scripts directory..."

# create a directory for bash scripts
sudo mkdir /usr/local/sh

echo "Downloading backup database shell script from S3..."

# Download the SQS Consumer Python script from S3
sudo aws s3 cp s3://${SCRIPTS_S3_BUCKET}/${BACKUP_DB_SCRIPT} /usr/local/sh/${BACKUP_DB_SCRIPT}
sudo chmod +x /usr/local/sh/${BACKUP_DB_SCRIPT}

# CREATE DATABASE (if it doesn't exist)
# # if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
# if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep ${DB_NAME}; then
#     echo "${DB_NAME} already EXISTS"
# else
#     echo "${DB_NAME} does NOT exist"
#     echo "Creating database ${DB_NAME}..."
#     sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER = postgres ENCODING = 'UTF-8';"
# fi

# Download restore database shell script from S3
sudo aws s3 cp s3://${SCRIPTS_S3_BUCKET}/${RESTORE_DB_SCRIPT} /usr/local/sh/${RESTORE_DB_SCRIPT}
sudo chmod +x /usr/local/sh/${RESTORE_DB_SCRIPT}

echo "Running restore_db.sh script..."

# Run the restore_db.sh script
sudo /usr/local/sh/${RESTORE_DB_SCRIPT} ${DB_NAME} ${BACKUP_BUCKET} ${AWS_REGION}

# # CREATE DATABASE (if it doesn't exist)
# if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep ${DB_NAME}; then
    echo "${DB_NAME} already EXISTS"
else
    echo "${DB_NAME} does NOT exist"
    echo "Creating database ${DB_NAME}..."
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER = postgres ENCODING = 'UTF-8';"
fi

# # CREATE DATABASE
# sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER = postgres ENCODING = 'UTF-8';"
# # sudo -u postgres psql -c "CREATE DATABASE dish_db3 OWNER = postgres ENCODING = 'UTF-8';"


# Create "pgcrypto" extension for generating UUIDs in PostgreSQL DB
sudo -u postgres psql -d ${DB_NAME} -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

# CREATE recipe_table IN DATABASE
sudo -u postgres psql ${DB_NAME} -c "
    CREATE TABLE IF NOT EXISTS recipe_table (
        dish_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        author TEXT,
        category JSONB,
        cook_time INTEGER,
        cuisine JSONB,
        description TEXT,
        host TEXT,
        image TEXT,
        ingredient_tags JSONB,
        ingredients JSONB,
        instructions JSONB,
        prep_time INTEGER,
        ratings FLOAT,
        sorted_ingredient_tags JSONB,
        timestamp INTEGER,
        title TEXT,
        total_time INTEGER,
        url TEXT UNIQUE,
        yields TEXT
    );"


# # CREATE recipe_table IN DATABASE
# sudo -u postgres psql ${DB_NAME} -c "
#     CREATE TABLE IF NOT EXISTS recipe_table2 (
#         dish_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
#         author TEXT,
#         category JSONB,
#         cook_time INTEGER,
#         cuisine JSONB,
#         description TEXT,
#         host TEXT,
#         image TEXT,
#         ingredient_tags JSONB,
#         ingredients JSONB,
#         instructions JSONB,
#         prep_time INTEGER,
#         ratings FLOAT,
#         sorted_ingredient_tags JSONB,
#         timestamp INTEGER,
#         title TEXT,
#         total_time INTEGER,
#         url TEXT UNIQUE,
#         yields TEXT
#     );"

# CREATE unique_ingredients_table IN DATABASE
sudo -u postgres psql ${DB_NAME} -c "
    CREATE TABLE IF NOT EXISTS unique_ingredients_table (
        ingredient_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        ingredient TEXT UNIQUE,
        count INTEGER
    );
    "

# # Add this query to create an index on the count column
# CREATE INDEX count_index ON unique_ingredients_table (count DESC);

# echo "Making usr/local/tmp directory for temporary backup files..."

# # Create a custom directory in /usr/local
# sudo mkdir /usr/local/tmp

# # grant appropriate permissions to usr/local/tmp directory to write temporary backup files
# sudo chmod -R a+rwx /usr/local/tmp
# # sudo chmod -R 755 /usr/local/tmp

# echo "Making shell scripts directory..."

# # create a directory for bash scripts
# sudo mkdir /usr/local/sh

# echo "Downloading backup database shell script from S3..."

# # Download the SQS Consumer Python script from S3
# sudo aws s3 cp s3://${SCRIPTS_S3_BUCKET}/${BACKUP_DB_SCRIPT} /usr/local/sh/${BACKUP_DB_SCRIPT}
# sudo chmod +x /usr/local/sh/${BACKUP_DB_SCRIPT}

# # Download restore database shell script from S3
# sudo aws s3 cp s3://${SCRIPTS_S3_BUCKET}/${RESTORE_DB_SCRIPT} /usr/local/sh/${RESTORE_DB_SCRIPT}
# sudo chmod +x /usr/local/sh/${RESTORE_DB_SCRIPT}
# echo "Running restore_db.sh script..."

# # Run the restore_db.sh script
# sudo /usr/local/sh/${RESTORE_DB_SCRIPT} ${DB_NAME} ${BACKUP_BUCKET} ${AWS_REGION}
# # Add cron job to run on the 5th minute of every hour
# echp "5 */1 * * * /usr/local/sh/${BACKUP_DB_SCRIPT}" ${DB_NAME} ${BACKUP_BUCKET} | crontab -
# echo "Adding cron job to run every 1 minutes..."
# echo "*/1 * * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} ${BACKUP_BUCKET}" | crontab -

#################################################
##### THIS IS THE CORRECT CRON JOB (BELOW) ######
#################################################

# echo "Adding backup db cron job to run once every day @ 9:10 AM..."
# echo "--> cron job backs up ${DB_NAME} to ${BACKUP_BUCKET} once every day at 9:10 AM"

# # Add cron job to run once a day (everyday) at 8:43 AM
# echo "43 8 * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} /usr/local/tmp ${BACKUP_BUCKET} 2>&1 | /usr/bin/logger -t backup_db_log" | crontab -

# # Add cron job to run once a day (everyday) at 9:10 AM
# echo "10 9 * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} /usr/local/tmp ${BACKUP_BUCKET} 2>&1 | /usr/bin/logger -t backup_db_log" | crontab -

# # Add cron job to run once a day (everyday) at 12:00 AM
# echo "0 0 * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} /usr/local/tmp ${BACKUP_BUCKET} 2>&1 | /usr/bin/logger -t backup_db_log" | crontab -

echo "Adding backup DB cron job to run every day at 9:00 AM..."
echo "--> cron job backs up ${DB_NAME} to ${BACKUP_BUCKET} to run every day at 9:00 AM"

# Add cron job to run every day at 9:00AM
# echo "0 9 * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} /usr/local/tmp ${BACKUP_BUCKET} 2>&1 | /usr/bin/logger -t backup_db_log" | crontab -

# # # Add cron job to run every 300 minutes
# echo "*/600 * * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} /usr/local/tmp ${BACKUP_BUCKET} 2>&1 | /usr/bin/logger -t backup_db_log" | crontab -

#################################################
##### THIS IS THE CORRECT CRON JOB (ABOVE) ######
#################################################
# echo "*/1 * * * * /usr/local/sh/${BACKUP_DB_SCRIPT} ${DB_NAME} /usr/local/tmp ${BACKUP_BUCKET} 2>&1 | /usr/bin/logger -t backup_db_log" | crontab -

# Create CSV file with headers
echo "last_modified,size,s3_bucket,s3_object_key,copy_complete" | sudo tee /usr/local/s3_downloads/s3_object_manifest.csv

echo "Making sqs_consumer directory..."

# create a directory for SQS consumer python script
sudo mkdir /usr/local/sqs_consumer

echo "Downloading SQS Consumer Python script from S3..."

# Download the SQS Consumer Python script from S3
sudo aws s3 cp s3://${SCRIPTS_S3_BUCKET}/${SQS_CONSUMER_PYTHON_SCRIPT} /usr/local/sqs_consumer/${SQS_CONSUMER_PYTHON_SCRIPT}
sudo chmod +x /usr/local/sqs_consumer/${SQS_CONSUMER_PYTHON_SCRIPT}

# path for S3 files to be downloaded to
S3_DOWNLOADS_PATH="/usr/local/s3_downloads"

# Environment variables need to be exported for main.py (SQS consumer) to use
# uses tee to write to the file with elevated privileges (sudo tee) also double quotes handle cases where the value contains spaces or special characters.

echo "Exporting environment variables to bashrc..."

echo DB_NAME=\"$DB_NAME\" >> ~/.bashrc

echo DB_USERNAME=\"$DB_USERNAME\" >> ~/.bashrc
echo DB_PASSWORD=\"$DB_PASSWORD\" >> ~/.bashrc

echo BACKUP_BUCKET=\"$BACKUP_BUCKET\" >> ~/.bashrc
echo BACKUP_DB_SCRIPT=\"$BACKUP_DB_SCRIPT\" >> ~/.bashrc

echo S3_DOWNLOADS_PATH=\"$S3_DOWNLOADS_PATH\" >> ~/.bashrc
echo SQS_QUEUE_URL=\"$SQS_QUEUE_URL\" >> ~/.bashrc
echo AWS_REGION=\"$AWS_REGION\" >> ~/.bashrc

echo "Exporting environment variables..."

# path for S3 files to be downloaded to
S3_DOWNLOADS_PATH="/usr/local/s3_downloads"

# Provide a print statement to show the value of DB_NAME
echo "Value of DB_NAME: ${DB_NAME}"
echo "Value of S3_DOWNLOADS_PATH: ${S3_DOWNLOADS_PATH}"
echo "Value of SQS_QUEUE_URL: ${SQS_QUEUE_URL}"
echo "Value of AWS_REGION: ${AWS_REGION}"

echo "Exporting using sudo tee"

echo "DB_NAME=${DB_NAME}" | sudo tee -a /etc/environment

echo "DB_USERNAME=${DB_USERNAME}" | sudo tee -a /etc/environment
echo "DB_PASSWORD=${DB_PASSWORD}" | sudo tee -a /etc/environment

echo "BACKUP_BUCKET=${BACKUP_BUCKET}" | sudo tee -a /etc/environment
echo "BACKUP_DB_SCRIPT=${BACKUP_DB_SCRIPT}" | sudo tee -a /etc/environment

echo "S3_DOWNLOADS_PATH=${S3_DOWNLOADS_PATH}" | sudo tee -a /etc/environment
echo "SQS_QUEUE_URL=${SQS_QUEUE_URL}" | sudo tee -a /etc/environment
echo "AWS_REGION=${AWS_REGION}" | sudo tee -a /etc/environment

# run source ~/.bashrc from sudo
source ~/.bashrc

source /etc/environment

# Provide a print statement to show the value of SQS_QUEUE_URL
echo "Value of SQS_QUEUE_URL: ${SQS_QUEUE_URL}"

# Provide a print statement to show the value of SQS_QUEUE_URL
echo "Giving python script execute permissions..."
echo "Python script to execute: ${SQS_CONSUMER_PYTHON_SCRIPT}"

# print echo statement stating that postgressql will be restarted
echo "Restarting PostgreSQL..."

# sudo service postgresql restart
sudo systemctl restart postgresql

# print statement stating that python script is being executed
echo "Sourcing bashrc and /etc/environment..."

# run source ~/.bashrc 
source ~/.bashrc

# run source /etc/environment
source /etc/environment

# print statement stating that python script is being executed
echo "Executing python script..."

# # # Run the Python script (SQS Consumer)
# DB_NAME=$DB_NAME \
# DB_USERNAME=$DB_USERNAME \
# DB_PASSWORD=$DB_PASSWORD \
# S3_DOWNLOADS_PATH=$S3_DOWNLOADS_PATH \
# SQS_QUEUE_URL=$SQS_QUEUE_URL \
# AWS_REGION=$AWS_REGION \
# python3 /usr/local/sqs_consumer/main.py

####################################################################
####################################################################
####################################################################

# # CREATE MAIN RECIPE TABLE IN DATABASE
# sudo -u postgres psql ${DB_NAME} -c "
#     CREATE TABLE recipe_table (
#         dish_id SERIAL PRIMARY KEY,
#         dish TEXT,
#         ingredients JSONB,
#         quantities JSONB,
#         directions JSONB,
#         url TEXT,
#         base_url TEXT,
#         img TEXT
#     );"

# # CREATE TABLE IN DATABASE
# sudo -u postgres psql ${DB_NAME} -c "
#     CREATE TABLE unique_ingredients_table (
#         ingredients_id SERIAL PRIMARY KEY,
#         ingredients TEXT,
#         count INTEGER
#     );"

# # CREATE TABLE IN DATABASE (OLD VERSION)
# sudo -u postgres psql ${DB_NAME} -c "
#     CREATE TABLE dish_table (
#         dish_id SERIAL PRIMARY KEY,
#         uid TEXT,
#         dish TEXT,
#         ingredients JSONB,
#         split_ingredients JSONB,
#         quantities JSONB,
#         directions JSONB
#     );"

# # create directions table (directions_table)
# sudo -u postgres psql ${DB_NAME} -c "
#     CREATE TABLE directions_table (
#         dish_id SERIAL PRIMARY KEY,
#         dish TEXT,
#         directions JSONB,
#         FOREIGN KEY (dish_id) REFERENCES dish_table(dish_id)
#     );"

# # create quantities table (quantities_table)
# sudo -u postgres psql ${DB_NAME} -c "
#     CREATE TABLE quantities_table (
#         dish_id SERIAL PRIMARY KEY,
#         dish TEXT,
#         quantities JSONB,
#         FOREIGN KEY (dish_id) REFERENCES dish_table(dish_id)
#     );"

# # Insert dish_id, dish, DIRECTIONS into directions_table from dish_table
# sudo -u postgres psql ${DB_NAME} -c "INSERT INTO directions_table (dish_id, dish, directions)
#     SELECT dish_id, dish, directions
#     FROM dish_table;"

# # Insert dish_id, dish, QUANTITIES into directions_table from dish_table
# sudo -u postgres psql ${DB_NAME} -c "INSERT INTO quantities_table (dish_id, dish, quantities)
#     SELECT dish_id, dish, quantities
#     FROM dish_table;"

# # Drop split_ingredients, quantities, directions from main dish_table
# sudo -u postgres psql ${DB_NAME} -c "ALTER TABLE dish_table
#     DROP COLUMN IF EXISTS quantities,
#     DROP COLUMN IF EXISTS directions,
#     DROP COLUMN IF EXISTS url,
#     DROP COLUMN IF EXISTS base_url,
#     DROP COLUMN IF EXISTS img;"

# # # Drop split_ingredients, quantities, directions from main dish_table
# # sudo -u postgres psql ${DB_NAME} -c "ALTER TABLE dish_table
# #     DROP COLUMN IF EXISTS quantities,
# #     DROP COLUMN IF EXISTS directions;"

# # sudo service postgresql restart
# sudo systemctl restart postgresql

####################################################################