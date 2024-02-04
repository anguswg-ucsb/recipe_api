#!/bin/bash

echo "The value of S3_BUCKET is: ${S3_BUCKET}"
echo "The value of DB_NAME is: ${DB_NAME}"

# Variables for SQS Consumer to use
echo "The value of SCRIPTS_S3_BUCKET is: ${SCRIPTS_S3_BUCKET}"
echo "The value of SQS Consumer python script is: ${SQS_CONSUMER_PYTHON_SCRIPT}"
echo "The SQS_QUEUE_URL is: ${SQS_QUEUE_URL}"

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

# CREATE DATABASE
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER = postgres ENCODING = 'UTF-8';"
# sudo -u postgres psql -c "CREATE DATABASE dish_db3 OWNER = postgres ENCODING = 'UTF-8';"
# sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER = postgres;"

# CREATE recipe_table IN DATABASE
sudo -u postgres psql ${DB_NAME} -c "
    CREATE TABLE recipe_table (
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
        title TEXT,
        total_time INTEGER,
        url TEXT,
        yields TEXT,
        dish_id BIGSERIAL PRIMARY KEY
    );"

# CREATE unique_ingredients_table IN DATABASE
sudo -u postgres psql ${DB_NAME} -c "
    CREATE TABLE unique_ingredients_table (
        ingredients_id BIGSERIAL PRIMARY KEY,
        ingredients TEXT
    );"

# Create CSV file with headers
echo "last_modified,size,s3_bucket,s3_object_key,copy_complete" | sudo tee /usr/local/s3_downloads/s3_object_manifest.csv

# create a directory for SQS consumer python script
sudo mkdir /usr/local/sqs_consumer

# Download the SQS Consumer Python script from S3
sudo aws s3 cp s3://${SCRIPTS_S3_BUCKET}/${SQS_CONSUMER_PYTHON_SCRIPT} /usr/local/sqs_consumer/${SQS_CONSUMER_PYTHON_SCRIPT}

# path for S3 files to be downloaded to
S3_DOWNLOADS_PATH="/usr/local/s3_downloads"

# Environment variables need to be exported for main.py (SQS consumer) to use
# uses tee to write to the file with elevated privileges (sudo tee) also double quotes handle cases where the value contains spaces or special characters.
echo "export DB_NAME=\"$DB_NAME\"" | sudo tee -a /etc/profile
echo "export S3_DOWNLOADS_PATH=\"$S3_DOWNLOADS_PATH\"" | sudo tee -a /etc/profile
echo "export SQS_QUEUE_URL=\"$SQS_QUEUE_URL\"" | sudo tee -a /etc/profile

# # Environment variables need to be exported for main.py (SQS consumer) to use
# # --> Sudo - Append the variable values (to /etc/profile)
# sudo sh -c "echo export DB_NAME=${DB_NAME} >> /etc/profile"
# sudo sh -c "echo export S3_DOWNLOADS_PATH=${S3_DOWNLOADS_PATH} >> /etc/profile"
# sudo sh -c "echo export SQS_QUEUE_URL=${SQS_QUEUE_URL} >> /etc/profile"
echo "export DB_NAME=$DB_NAME" >> ~/.bashrc
echo 'export DB_NAME=$DB_NAME' >> ~/.bashrc
echo 'export S3_DOWNLOADS_PATH="$S3_DOWNLOADS_PATH"' >> ~/.bashrc
echo 'export S3_DOWNLOADS_PATH=$S3_DOWNLOADS_PATH' >> ~/.bashrc
echo 'export SQS_QUEUE_URL=$SQS_QUEUE_URL' >> ~/.bashrc

# # Append the variable values (to /etc/profile)
# echo export DB_NAME=${DB_NAME} >> /etc/profile
# echo export S3_DOWNLOADS_PATH="/usr/local/s3_downloads" >> /etc/profile
# echo export SQS_QUEUE_URL=${SQS_QUEUE_URL} >> /etc/profile

# # Export env vars (to .bashrc)
# echo export DB_NAME=${DB_NAME} >> ~/.bashrc
# echo export S3_DOWNLOADS_PATH="/usr/local/s3_downloads" >> ~/.bashrc
# echo export SQS_QUEUE_URL=${SQS_QUEUE_URL} >> ~/.bashrc

# # Export env vars (with escaped double quotes)
# echo "export DB_NAME=\"$DB_NAME\"" >> /etc/profile
# echo export S3_DOWNLOADS_PATH="/usr/local/s3_downloads" >> /etc/profile
# echo "export SQS_QUEUE_URL=\"$SQS_QUEUE_URL\"" >> /etc/profile

# # export environment variables for main.py (SQS consumer) to use
# export DB_NAME=${DB_NAME}
# export S3_DOWNLOADS_PATH="/usr/local/s3_downloads"
# export SQS_QUEUE_URL=${SQS_QUEUE_URL}

echo "DB_NAME=${DB_NAME}" | sudo tee -a /etc/environment
echo "S3_DOWNLOADS_PATH=${S3_DOWNLOADS_PATH}" | sudo tee -a /etc/environment
echo "SQS_QUEUE_URL=${SQS_QUEUE_URL}" | sudo tee -a /etc/environment

echo DB_NAME=\"$DB_NAME\" >> /etc/environment
echo S3_DOWNLOADS_PATH=\"$S3_DOWNLOADS_PATH\" >> /etc/environment
echo SQS_QUEUE_URL=\"$SQS_QUEUE_URL\" >> /etc/environment

echo "Exporting using sudo tee"

echo DB_NAME=\"$DB_NAME\" | sudo tee -a /etc/environment
echo S3_DOWNLOADS_PATH=\"$S3_DOWNLOADS_PATH\" | sudo tee -a /etc/environment
echo SQS_QUEUE_URL=\"$SQS_QUEUE_URL\" | sudo tee -a /etc/environment

# Provide a print statement to show the value of SQS_QUEUE_URL
echo "The SQS_QUEUE_URL is: ${SQS_QUEUE_URL}"

# Provide a print statement to show the value of SQS_QUEUE_URL
echo "Giving python script execute permissions..."
echo "Python script to execute: ${SQS_CONSUMER_PYTHON_SCRIPT}"

python3 /usr/local/sqs_consumer/${SQS_CONSUMER_PYTHON_SCRIPT}
python3 /usr/local/sqs_consumer/main.py

# print statement stating that python script is being executed
echo "Executing python script..."
DB_NAME=$DB_NAME S3_DOWNLOADS_PATH=$S3_DOWNLOADS_PATH SQS_QUEUE_URL=$SQS_QUEUE_URL AWS_REGION=$AWS_REGION python3 /usr/local/sqs_consumer/main.py

# print echo statement stating that postgressql will be restarted
echo "Restarting PostgreSQL..."

# sudo service postgresql restart
sudo systemctl restart postgresql

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