#!/bin/bash

echo "The value of S3_BUCKET is: ${S3_BUCKET}"
echo "The value of DB_NAME is: ${DB_NAME}"

# update 
sudo apt-get update -y && sudo apt-get upgrade -y

#  download AWS CLI
sudo apt-get install awscli -y

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

# sudo service postgresql restart
sudo systemctl restart postgresql

####################################################################