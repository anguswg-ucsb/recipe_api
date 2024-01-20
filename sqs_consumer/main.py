#!/usr/bin/env python3

# General utility libraries
import subprocess
import json
import os
import time

# AWS SDK for Python
import boto3

# Pandas for data manipulation
import pandas as pd

# Environment variables
DB_NAME           = os.environ.get("DB_NAME")

DB_USERNAME       = os.environ.get("DB_USERNAME")
DB_PASSWORD       = os.environ.get("DB_PASSWORD")

S3_DOWNLOADS_PATH = os.environ.get("S3_DOWNLOADS_PATH")
SQS_QUEUE_URL     = os.environ.get("SQS_QUEUE_URL")
AWS_REGION        = os.environ.get("AWS_REGION")

print(f"---->\n Value of DB_NAME: {DB_NAME}")
print(f"---->\n Value of S3_DOWNLOADS_PATH: {S3_DOWNLOADS_PATH}")
print(f"---->\n Value of SQS_QUEUE_URL: {SQS_QUEUE_URL}")

if DB_USERNAME:
    print(f"---->\n DB_USERNAME WAS FOUND")

if DB_PASSWORD:
    print(f"---->\n DB_PASSWORD WAS FOUND")

# execute_upsert_script()
def upsert_recipe_csv_into_db(db_name, csv_path, target_table, staging_table):
    
    # csv_path = "/usr/local/s3_downloads/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv"
    # target_table = "recipe_table"
    # staging_table = "staging_recipe_table"
    # db_name = "recipe_db"

    # create insert_cols string for INSERT INTO clause
    insert_cols = "author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, timestamp, title, total_time, url, yields"
    
    # create update_cols string for ON CONFLICT DO UPDATE SET clause (based on insert_cols)
    update_cols = "\t" + ",\n\t".join([f"{i} = EXCLUDED.{i}" for i in insert_cols.split(", ")])

    temp_table_cols = f"""
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
            """
    
    # print(f"=====\n{update_cols}\n=======")
    # psql upsert command
    # Make a temporary table that is a copy of the target table
    # Copy the CSV into the temporary table
    # Insert the temporary table data into the target table
    # On conflict, (UNIQUE url constraint is violated) update the target table with the temporary table data to 
    # ensure there are no duplicates in the target table based on the "url" column
    psql_upsert = f"""
    BEGIN;
        CREATE TEMPORARY TABLE {staging_table} ({temp_table_cols});
        
        COPY {staging_table} ({insert_cols}) from '{csv_path}' with DELIMITER ',' CSV HEADER;

        INSERT INTO {target_table} ({insert_cols}) 
        SELECT {insert_cols} 
        FROM {staging_table} 
        ON CONFLICT (url) 
        DO UPDATE SET 
            {update_cols}
        RETURNING *;
        DROP TABLE {staging_table};
    COMMIT;
    """

    # print(f"======\n{psql_upsert}")
    # # psql upsert command
    # # Make a temporary table that is a copy of the target table
    # # Copy the CSV into the temporary table
    # # Insert the temporary table data into the target table
    # # On conflict, (UNIQUE url constraint is violated) update the target table with the temporary table data to 
    # # ensure there are no duplicates in the target table based on the "url" column
    # psql_upsert = f"""
    # BEGIN;
    #     CREATE TEMPORARY TABLE {staging_table} (LIKE {target_table});
        
    #     COPY {staging_table} ({insert_cols}) from '{csv_path}' with DELIMITER ',' CSV HEADER;

    #     INSERT INTO {target_table} ({insert_cols}) 
    #     SELECT {insert_cols} 
    #     FROM {staging_table} 
    #     ON CONFLICT (url) 
    #     DO UPDATE SET 
    #         {update_cols};

    #     DROP TABLE {staging_table};
    # COMMIT;
    # """

    print(f"======\n{psql_upsert}")
    
    # Build command to upsert new rows into database 
    upsert_command = ['sudo', '-u', 'postgres', 'psql', '-d', db_name, '-c', psql_upsert]
    print(f"upsert_command:\n - '{' '.join(upsert_command)}'")
    
    # Run the Bash script as a string
    try:
        # subprocess.run(["bash", "-c", bash_script], shell=True)
        upsert_output = subprocess.run(upsert_command,  capture_output=True, text=True)

        print(f"upsert_output: {upsert_output}")
        print(f"upsert_output.stdout: {upsert_output.stdout}")
        if upsert_output.returncode != 0:
            print(f"ERROR: Upsert command failed with return code {upsert_output.returncode}")
            print(f"stderr: {upsert_output.stderr}")
        print(f"=====" * 8)
    except Exception as e:
        print(f"Exception raised while running psql upsert_command\n{e}")
        print(f"ERROR upsert_command:\n - '{' '.join(upsert_command)}'")

def create_and_upsert_unique_ingredients_data(csv_path):

    # csv_path = "/Users/anguswatters/Desktop/s3_downloads/9d01169a86e24fb8867823a6fcd249a6_1705762724.csv"
    
    # os.dirpaths(csv_path)

    # get filename from path
    filename = os.path.basename(csv_path)
    dir_path = os.path.dirname(csv_path)
    
    # make a temporary filename
    output_filename = filename.replace(".csv", "_unique_ingredients.csv")
    output_path = os.path.join(dir_path, output_filename)

    # read in CSV into pandas dataframe
    df = pd.read_csv(csv_path)

    # create unique ingredients dataframe
    unique_ingreds = create_unique_ingredients(df)

    # save unique ingredients dataframe to csv
    unique_ingreds[["ingredient", "count"]].to_csv(output_path, index=False)

    # upsert unique ingredients into database
    upsert_unique_ingredients_into_db(DB_NAME, output_path, "unique_ingredients_table", "staging_unique_ingredients_table")


# From a local CSV file, extract the count of unique ingredients in the CSV and upsert new rows into a database table
def upsert_unique_ingredients_into_db(db_name, csv_path, target_table, staging_table):
    
    # csv_path = "/usr/local/s3_downloads/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv"
    # target_table = "unique_ingredients_table"
    # staging_table = "staging_unique_ingredients_table"
    # db_name = "recipe_db"
    # ingredients_id BIGSERIAL PRIMARY KEY,
    # ingredients TEXT,
    # count INTEGER
    # ingredient_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    # ingredient TEXT,
    # count INTEGER

    # create insert_cols string for INSERT INTO clause
    # insert_cols = "ingredient_id, ingredient, count"
    insert_cols = "ingredient, count"
    
    # create update_cols string for ON CONFLICT DO UPDATE SET clause (based on insert_cols)
    update_cols = "\t" + ",\n\t".join([f"{i} = EXCLUDED.{i}" for i in insert_cols.split(", ")])

    temp_table_cols = f"""
            ingredient TEXT UNIQUE,
            count INTEGER
            """

    # Make a temporary table that is a copy of the target table
    # Copy the CSV into the temporary table
    # Insert the temporary table data into the target table
    # On conflict, (UNIQUE ingredient constraint is violated) update the target table by incrementing the count in the table 
    # with the value in the count column of the temporary table with the temporary table data to 
    # if the ingredient does NOT already exists in the target table, then insert the ingredient into the target table 
    # with the count value from the temporary table
    psql_upsert = f"""
    BEGIN;
        CREATE TEMPORARY TABLE {staging_table} ({temp_table_cols});
        
        COPY {staging_table} ({insert_cols}) from '{csv_path}' with DELIMITER ',' CSV HEADER;

        INSERT INTO {target_table} ({insert_cols}) 
        SELECT {insert_cols} 
        FROM {staging_table} 
        ON CONFLICT (ingredient) 
        DO UPDATE SET 
            {update_cols}
        RETURNING *;
        DROP TABLE {staging_table};
    COMMIT;
    """

    print(f"======\n{psql_upsert}")
    
    # Build command to upsert new rows into database 
    upsert_command = ['sudo', '-u', 'postgres', 'psql', '-d', db_name, '-c', psql_upsert]
    print(f"upsert_command:\n - '{' '.join(upsert_command)}'")
    
    # Run the Bash script as a string
    try:
        # subprocess.run(["bash", "-c", bash_script], shell=True)
        upsert_output = subprocess.run(upsert_command,  capture_output=True, text=True)

        print(f"upsert_output: {upsert_output}")
        print(f"upsert_output.stdout: {upsert_output.stdout}")
        if upsert_output.returncode != 0:
            print(f"ERROR: Upsert command failed with return code {upsert_output.returncode}")
            print(f"stderr: {upsert_output.stderr}")
        print(f"=====" * 8)
    except Exception as e:
        print(f"Exception raised while running psql upsert_command\n{e}")
        print(f"ERROR upsert_command:\n - '{' '.join(upsert_command)}'")

#################################################################        
#################################################################
        
def create_unique_ingredients(df, json_column = "ingredient_tags"):
    """Create unique ingredients dataset

    Args:
        df (pandas.DataFrame): Raw NER dataset

    Returns:
        pandas.DataFrame: Unique ingredients dataset
    """

    # df = recipes2.head(5)

    # # convert json dictionary column to dictionary and then list
    # df['ingredients'].apply(json.loads)

    # #########################
    # df = recipe_df
    # json_column = "ingredient_tags"
    # #########################

    # Select just ingredients column
    df = df[[json_column]]

    # convert json dictionary column to dictionary and then list
    df[json_column] = df[json_column].apply(lambda row: json.loads(row)[json_column])
    # df["ingredients"] = df["ingredients"].apply(lambda row: json.loads(row)['ingredients'])

    # explode "ingredients" list column to make an individual row for each ingredients in each dish
    df = df.explode([json_column]).reset_index(drop=True)
    # df = df.explode(['ingredients']).reset_index(drop=True)

    # replace whitespace with single space
    df[json_column] = df[json_column].replace(r'\s+', ' ', regex=True)
    # df["ingredients"] = df["ingredients"].replace(r'\s+', ' ', regex=True)

    # convert all characters in 'ingredients' to lowercase
    df[json_column] = df[json_column].str.lower()
    # df['ingredients'] = df['ingredients'].str.lower()

    # CREATE FREQUENCY DATAFRAME
    # ingreds_df = df[["ingredients"]]
    freq_df = df[[json_column]].value_counts()
    # freq_df = df[["ingredients"]].value_counts()

    # convert series to dataframe
    freq_df = pd.DataFrame(freq_df)

    # reset index
    freq_df = freq_df.reset_index()

    # select unique ingredients
    unique_ingreds = df[[json_column]].drop_duplicates(subset=[json_column], keep='first')
    # unique_ingreds = df[["ingredients"]].drop_duplicates(subset=['ingredients'], keep='first')

    # merge counts with unique ingredients
    unique_ingreds = pd.merge(unique_ingreds, freq_df, on=json_column, how='left')
    # unique_ingreds = pd.merge(unique_ingreds, freq_df, on='ingredients', how='left')

    # replace NaN values with 0
    unique_ingreds['count'].fillna(0, inplace=True)

    # Convert the 'float_column' to an integer
    unique_ingreds['count'] = unique_ingreds['count'].astype(int)

    # sort unique_ingreds by count in descending order
    unique_ingreds = unique_ingreds.sort_values(by='count', ascending=False)

    # add unique id for each ingredient
    unique_ingreds["ingredient_id"] = unique_ingreds.index

    # rename json_column to "ingredient"
    unique_ingreds = unique_ingreds.rename(columns={json_column: "ingredient"})
    
    # reorder columns
    unique_ingreds = unique_ingreds[["ingredient_id", "ingredient", "count"]]
    # unique_ingreds = unique_ingreds[["ingredient_id", json_column, "count"]]

    # # save unique ingredients dataframe to csv
    # unique_ingreds[["ingredients_id", "ingredients", "count"]].to_csv('data/unique_ingredients.csv', index=False)

    return unique_ingreds

# import pandas as pd
# import boto3
# import json

# s3_bucket = "recipes-output-bucket"
# s3_object_key = "9d01169a86e24fb8867823a6fcd249a6_1705762724.csv"
# local_file_path = f"/Users/anguswatters/Desktop/s3_downloads/{s3_object_key}"

# s3 = boto3.client("s3", region_name="us-west-1")
# s3_obj = s3.download_file(Bucket=s3_bucket, Key=s3_object_key, Filename=local_file_path)

# recipe_df = pd.read_csv(local_file_path)

# [list(set(json.loads(i)["ingredient_tags"])) for i in df['ingredient_tags'].values.tolist()]
# df = recipe_df

#################################################################
#################################################################

def upsert_s3_data_into_db(client, s3_bucket, s3_object_key, local_file_path): 
    # Download the object from S3
    # msg_body = json.loads(msg["Body"])

    # s3_bucket = msg_body["Records"][0]["s3"]["bucket"]["name"]
    # s3_object_key = msg_body["Records"][0]["s3"]["object"]["key"]
    # local_file_path = f"s3_downloads/{s3_object_key}"
    # client = s3

    try:
        s3_obj = client.download_file(Bucket=s3_bucket, Key=s3_object_key, Filename=local_file_path)
        print(f"Successfully downloaded {s3_object_key}\n - FROM: {s3_bucket}\n - TO: {local_file_path}")
    except Exception as e:
        print(f"Exception raised while downloading {s3_object_key} from {s3_bucket}:\n{e}")
        return
    
    print(f"Trying to UPSERT {local_file_path} into 'recipe_table' in database...")
    
    print(f"===========================")
    print(f"==== ATTEMPT to UPSERT (into recipe_table) ====")
    print(f"==== Trying to UPSERT {local_file_path} into 'recipe_table' in database ====")
    print(f"===========================")

    # Try and execute the upsert script
    # upsert_csv_into_db(DB_NAME, local_file_path, "recipe_table", "staging_recipe_table")
    upsert_recipe_csv_into_db(DB_NAME, local_file_path, "recipe_table", "staging_recipe_table")

    # execute_upsert_script(DB_NAME, local_file_path, "recipe_table", "staging_recipe_table")

    print(f"-----> Succesfully UPSERTED {local_file_path} into 'recipe_table' database!")
    print(f"=====" * 8)

    print(f"===========================")
    print(f"==== ATTEMPT to UPSERT (into recipe_table2) ====")
    print(f"==== Trying to UPSERT {local_file_path} into 'recipe_table2' in database ====")
    print(f"===========================")

    # Try and execute the upsert script
    # upsert_csv_into_db(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")
    upsert_recipe_csv_into_db(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")

    # execute_upsert_script(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")

    print(f"----> Succesfully UPSERTED {local_file_path} into 'recipe_table2' database!")
    
    print(f"=====" * 8)
    print(f"=====" * 8)

    ################### ALL GOOD TO GO ##############################
    print(f"Sleeping for 3 seconds...")

    time.sleep(5)

    print(f"Deleting local file {local_file_path}...")

    # Delete the local file
    subprocess.run(f"rm {local_file_path}", shell=True)

    return 

# def upsert_unique_ingreds_into_db(db_name, local_file_path, target_table, staging_table):


def main() -> None:

    s3 = boto3.client("s3", region_name=AWS_REGION)
    sqs = boto3.client("sqs", region_name=AWS_REGION)

    empty_response_count = 0  # Initialize the count of consecutive empty responses

    while True:
        print(f"---- STARTING NEW POLLING ITERATION ----")
        print(f"empty_response_count: {empty_response_count}")

        # Long poll for message on SQS queue
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=3,
            WaitTimeSeconds=20
        )

        # Get the messages from the response or default to an empty list
        messages = response.get("Messages", [])

        if not messages:
            empty_response_count += 1
            print(f"No messages to process. Empty response count: {empty_response_count}. Exiting...")
            # Increase sleep time with each consecutive empty response
            # sleep_time = min(2**empty_response_count, 60)
            sleep_time = min(2*empty_response_count, 60)
            print(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            continue
        else:
            # Reset the consecutive empty response count
            empty_response_count = 0
        
        message_count = 0

        for msg in messages:
            print(f"msg: {msg}")
            print(f"Processing message {message_count + 1} of {len(messages)}")

            msg_body = json.loads(msg["Body"])

            if "Records" not in msg_body:
                print(f"Records key not found in message body. Skipping...")
                continue
            # if msg_body["Event"] == "s3:TestEvent":
            #     print(f"s3:TestEvent message. Skipping...")
            #     continue
    
            s3_bucket = msg_body["Records"][0]["s3"]["bucket"]["name"]
            s3_object_key = msg_body["Records"][0]["s3"]["object"]["key"]
            local_file_path = f"{S3_DOWNLOADS_PATH}/{s3_object_key}"

            print(f"---" * 5)
            print(f"s3_bucket: {s3_bucket}")
            print(f"s3_object_key: {s3_object_key}")
            print(f"local_file_path: {local_file_path}")
            print(f"---" * 5)
            print(f"Attempting download and insert of S3 CSV...")

            # Download the object from S3, copy it into the database, and delete the local file
            # insert_s3_obj_into_db(s3, s3_bucket, s3_object_key, local_file_path)
            upsert_s3_data_into_db(s3, s3_bucket, s3_object_key, local_file_path)

            print(f"Successfully downloaded and inserted S3 CSV!")

            recipes_df = pd.read_csv(local_file_path)

            # Create unique ingredients dataset
            unique_ingreds = create_unique_ingredients(recipes_df, json_column = "ingredient_tags")


            # TODO: If successful, delete the message from the SQS queue
            # sqs.delete_message(
            #     QueueUrl=SQS_QUEUE_URL,
            #     ReceiptHandle=msg["ReceiptHandle"]
            # )
            

            print(f"====" * 7)
            print(f"====" * 7)

# Create a /copy command to copy CSV into a specified database table
def create_slash_copy_cmd(db_name, table_name, csv_path):
    copy_cols = "author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, timestamp, title, total_time, url, yields"
    
    copy_command= f'\copy {table_name} ({copy_cols}) FROM \'{csv_path}\' DELIMITER \',\' CSV HEADER;'
    
    return copy_command


################### ALL GOOD TO GO ##############################
# def insert_s3_obj_into_db(client, s3_bucket, s3_object_key, local_file_path): 
#     # Download the object from S3
#     # msg_body = json.loads(msg["Body"])

#     # s3_bucket = msg_body["Records"][0]["s3"]["bucket"]["name"]
#     # s3_object_key = msg_body["Records"][0]["s3"]["object"]["key"]
#     # local_file_path = f"s3_downloads/{s3_object_key}"
#     # client = s3

#     try:
#         s3_obj = client.download_file(Bucket=s3_bucket, Key=s3_object_key, Filename=local_file_path)
#         print(f"Successfully downloaded {s3_object_key}\n - FROM: {s3_bucket}\n - TO: {local_file_path}")
#     except Exception as e:
#         print(f"Exception raised while downloading {s3_object_key} from {s3_bucket}:\n{e}")
#         return
    
#     # Copy the CSV from S3 to local file system
#     s3_copy_command =  f'aws s3 cp s3://{s3_bucket}/{s3_object_key} {local_file_path}'
    
#     print(f"s3_copy_command:\n{s3_copy_command}")

#     ################### ALL GOOD TO GO ##############################
#     # # =======================================
#     # # ATTEMPT AT COPY 1
#     # # =======================================
#     # print(f"===========================")
#     # print(f"==== ATTEMPT AT COPY 1 ====")
#     # print(f"===========================")

#     # # create copy command to copy csv into database recipe_table
#     # copy_command= f'\copy recipe_table FROM \'{local_file_path}\' DELIMITER \',\' CSV HEADER;'
#     # # copy_command = f'\"\\copy recipe_table FROM \'{local_file_path}\' DELIMITER \',\' CSV HEADER;"'
#     # # f'sudo -u postgres psql -d {"recipe_db"} -c "\\copy recipe_table FROM \'{"/usr/local/s3_downloads/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv"}\' DELIMITER \',\' CSV HEADER;"'
    
#     # print(f"Copying file {local_file_path} into database (1)...")
#     # print(f"copy_command:\n{copy_command}")
#     # print("---> Running following command: \n" + " ".join(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command]))

#     # # copy dish recipes CSV into recipe_table
#     # copy1_output = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command],  capture_output=True, text=True)

#     # print(f"copy1_output: {copy1_output}")
#     # print(f"copy1_output.stdout: {copy1_output.stdout}")
#     # print(f"=========================")

#     # # =======================================
#     # # ATTEMPT AT COPY 2
#     # # =======================================

#     print(f"===========================")
#     print(f"==== ATTEMPT AT COPY 2 (into recipe_table) ====")
#     print(f"===========================")

#     copy_command2= f'\copy recipe_table (author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, title, total_time, url, yields) FROM \'{local_file_path}\' DELIMITER \',\' CSV HEADER;'

#     print(f"Copying file {local_file_path} into database (2)...")
#     print(f"copy_command2:\n{copy_command2}")
#     print("---> Running following command: \n" + " ".join(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command2]))

#     # copy dish recipes CSV into recipe_table
#     copy2_output = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command2],  capture_output=True, text=True)

#     print(f"copy2_output: {copy2_output}")
#     print(f"copy2_output.stdout: {copy2_output.stdout}")
#     print(f"=====" * 8)

#     # # =======================================
#     # # ATTEMPT AT COPY 3 (into recipe_table2)
#     # # =======================================

#     print(f"===========================")
#     print(f"==== ATTEMPT AT COPY 3 (into recipe_table2) ====")
#     print(f"===========================")

#     copy_command3 = f'\copy recipe_table2 (author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, title, total_time, url, yields) FROM \'{local_file_path}\' DELIMITER \',\' CSV HEADER;'

#     print(f"Copying file {local_file_path} into database (recipe_table2)...")
#     print(f"copy_command3:\n{copy_command3}")
#     print("---> Running following command: \n" + " ".join(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command3]))

#     # copy dish recipes CSV into recipe_table
#     copy3_output = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command3],  capture_output=True, text=True)

#     print(f"copy3_output: {copy3_output}")
#     print(f"copy3_output.stdout: {copy3_output.stdout}")
#     print(f"=====" * 8)
#     print(f"=====" * 8)

#     # # =======================================

#     ################### ALL GOOD TO GO ##############################
#     print(f"Sleeping for 3 seconds...")

#     time.sleep(5)
#     # sudo -u postgres psql -d recipe_db -c "\copy recipe_table FROM 'usr/local/s3_downloads/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv' DELIMITER ',' CSV HEADER;"
#     print(f"Deleting local file {local_file_path}...")
#     # aws s3 cp s3://recipes-output-bucket/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv /usr/local/s3_downloads/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv 
#     # Delete the local file
#     subprocess.run(f"rm {local_file_path}", shell=True)

if __name__ == "__main__":
    main()


# # execute_upsert_script()
# def execute_upsert_script(db_name, csv_path, target_table, staging_table):

#     bash_script = f"""
#     #!/bin/bash
#     # Set your PostgreSQL credentials
#     DATABASE_NAME="{db_name}"

#     # Set your CSV file path
#     CSV_FILE="{csv_path}"

#     # Set your destination table and staging table
#     DESTINATION_TABLE="{target_table}"
#     STAGING_TABLE="{staging_table}"

#     # # Create a temporary staging table
#     # sudo -u postgres psql -d "$DATABASE_NAME" -c "CREATE TEMPORARY TABLE $STAGING_TABLE (LIKE $DESTINATION_TABLE);"

#     # Create a persistent staging table if not exists
#     sudo -u postgres psql -d "$DATABASE_NAME" -c "CREATE TABLE IF NOT EXISTS $STAGING_TABLE (LIKE $DESTINATION_TABLE);"

#     # Truncate (empty) the staging table
#     sudo -u postgres psql -d "$DATABASE_NAME" -c "TRUNCATE TABLE $STAGING_TABLE;"

#     # # Copy data from CSV to the temporary staging table
#     # cat "$CSV_FILE" | sudo -u postgres psql -d "$DATABASE_NAME" -c "COPY $STAGING_TABLE (author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, title, total_time, url, yields) FROM STDIN WITH CSV;"
    
#     # Copy data from CSV to the temporary staging table
#     sudo -u postgres psql -d "$DATABASE_NAME" -c "\copy $STAGING_TABLE (author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, title, total_time, url, yields) FROM '$CSV_FILE' DELIMITER ',' CSV;"

#     # Perform upsert from the staging table to the destination table
#     sudo -u postgres psql -d "$DATABASE_NAME" -c "
#         INSERT INTO $DESTINATION_TABLE (author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, title, total_time, url, yields)
#         SELECT author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, title, total_time, url, yields
#         FROM $STAGING_TABLE
#         ON CONFLICT (url)
#         DO UPDATE SET
#             author = EXCLUDED.author,
#             category = EXCLUDED.category,
#             cook_time = EXCLUDED.cook_time,
#             cuisine = EXCLUDED.cuisine,
#             description = EXCLUDED.description,
#             host = EXCLUDED.host,
#             image = EXCLUDED.image,
#             ingredient_tags = EXCLUDED.ingredient_tags,
#             ingredients = EXCLUDED.ingredients,
#             instructions = EXCLUDED.instructions,
#             prep_time = EXCLUDED.prep_time,
#             ratings = EXCLUDED.ratings,
#             sorted_ingredient_tags = EXCLUDED.sorted_ingredient_tags,
#             title = EXCLUDED.title,
#             total_time = EXCLUDED.total_time,
#             yields = EXCLUDED.yields;
#     "

#     # # Clean up: Drop the temporary staging table
#     # sudo -u postgres psql -d "$DATABASE_NAME" -c "DROP TABLE $STAGING_TABLE;"

#     # Truncate (empty) the staging table again
#     sudo -u postgres psql -d "$DATABASE_NAME" -c "TRUNCATE TABLE $STAGING_TABLE;"
#     """

#     # Run the Bash script as a string
#     try:
#         # subprocess.run(["bash", "-c", bash_script], shell=True)
#         subprocess.run([bash_script], shell=True)
#     except Exception as e:
#         print(f"Exception raised while running bash script SHELL == TRUE:\n{e}")

#     # subprocess.run(["bash", "-c", bash_script], shell=True)
    
#     try:
#         # copy_output = subprocess.run(["bash", "-c", bash_script], capture_output=True, text=True)
#         copy_output = subprocess.run([bash_script], capture_output=True, text=True)
#         print(f"copy_output: {copy_output}")
#         print(f"copy_output.stdout: {copy_output.stdout}")
#     except Exception as e:
#         print(f"Exception raised while running bash script SHELL == FALSE:\n{e}")


# #     copy2_output = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-d', DB_NAME, '-c', copy_command2],  capture_output=True, text=True)

# #     print(f"copy2_output: {copy2_output}")
# #     print(f"copy2_output.stdout: {copy2_output.stdout}")
#     # # Path to the Bash script
#     # bash_script_path = "usr/local/upsert_csv_into_db.sh"

#     # # Run the Bash script
#     # subprocess.run(["bash", bash_script_path])
        
# # # execute_upsert_script()
# # def upsert_csv_into_db(db_name, csv_path, target_table, staging_table):
    
# #     # csv_path = "/usr/local/s3_downloads/5de1e187030a4ac5a57b66e207c70fd2_1705444862.csv"
# #     # target_table = "recipe_table"
# #     # staging_table = "staging_recipe_table"
# #     # db_name = "recipe_db"

# #     insert_cols = "author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, timestamp, title, total_time, url, yields"

# #     # # psql upsert command
# #     # psql_upsert = f"""
# #     # CREATE TEMPORARY TABLE {staging_table} (LIKE {target_table});
    
# #     # COPY {staging_table} ({insert_cols}) from '{csv_path}' with DELIMITER ',' CSV HEADER;

# #     # DELETE from {target_table} USING {staging_table} WHERE {target_table}.url = {staging_table}.url;

# #     # INSERT INTO {target_table} ({insert_cols}) SELECT {insert_cols} FROM {staging_table};

# #     # DROP TABLE {staging_table};
# #     # """

# #     # # psql upsert command
# #     psql_upsert = f"""
# #     BEGIN;
# #         CREATE TEMPORARY TABLE {staging_table} (LIKE {target_table});
        
# #         COPY {staging_table} ({insert_cols}) from '{csv_path}' with DELIMITER ',' CSV HEADER;

# #         DELETE from {target_table} USING {staging_table} WHERE {target_table}.url = {staging_table}.url;

# #         INSERT INTO {target_table} ({insert_cols}) SELECT {insert_cols} FROM {staging_table};

# #         DROP TABLE {staging_table};
# #     COMMIT;
# #     """

# #     # # psql upsert command
# #     # psql_upsert = f"""CREATE TEMPORARY TABLE {staging_table} (LIKE {target_table});
    
# #     # COPY {staging_table} ({insert_cols}) from {csv_path} with DELIMITER ',' CSV HEADER;

# #     # DELETE from {target_table} USING {staging_table} WHERE {target_table}.url = {staging_table}.url AND {target_table}.timestamp = {staging_table}.timestamp;

# #     # INSERT INTO {target_table} ({insert_cols}) SELECT {insert_cols} FROM {staging_table};

# #     # DROP TABLE {staging_table};
# #     # """
    
# #     # Final command to run
# #     upsert_command = ['sudo', '-u', 'postgres', 'psql', '-d', db_name, '-c', psql_upsert]
# #     print(f"upsert_command:\n - '{' '.join(upsert_command)}'")
    
# #     # Run the Bash script as a string
# #     try:
# #         # subprocess.run(["bash", "-c", bash_script], shell=True)
# #         upsert_output = subprocess.run(upsert_command,  capture_output=True, text=True)

# #         print(f"upsert_output: {upsert_output}")
# #         print(f"upsert_output.stdout: {upsert_output.stdout}")
# #         if upsert_output.returncode != 0:
# #             print(f"ERROR: Upsert command failed with return code {upsert_output.returncode}")
# #             print(f"stderr: {upsert_output.stderr}")
# #         print(f"=====" * 8)
# #     except Exception as e:
# #         print(f"Exception raised while running psql upsert_command\n{e}")
# #         print(f"ERROR upsert_command:\n - '{' '.join(upsert_command)}'")
