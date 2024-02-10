#!/usr/bin/env python3

# General utility libraries
import subprocess
import json
import os
import time
import csv
from collections import defaultdict

# AWS SDK for Python
import boto3

# Pandas for data manipulation
import pandas as pd

# --------------------------------
# ---- Recipes data functions ----
# functions for upserting new CSV data into database from an SQS queue
# --------------------------------
    
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
        else:

            try: 
                print(f"---" * 5)
                print(f"------ TRYING TO LOOK AT RECIPES UPDATES COUNTS -------")
                print(f"---" * 5)
                # Parse the output to determine inserted and updated rows
                rows_affected = upsert_output.stdout.strip().split('\n')
                inserted_rows = [row.split('\t') for row in rows_affected if "INSERT 0 1" in row]
                updated_rows = [row.split('\t') for row in rows_affected if "UPDATE 1" in row]

                print(f"Inserted Rows: {inserted_rows}")
                print(f"Updated Rows: {updated_rows}")
                print(f"---" * 5)
            except Exception as e:
                print(f"Exception raised while parsing upsert output:\n{e}")
        print(f"=====" * 8)
    except Exception as e:
        print(f"Exception raised while running psql upsert_command\n{e}")
        print(f"ERROR upsert_command:\n - '{' '.join(upsert_command)}'")

# --------------------------------------
# ---- Unique ingredients functions ----
# From new recipes CSV file (saved locally) extract all of the unique ingredients and upsert them into the database)
# --------------------------------------
        
def create_and_upsert_unique_ingredients_data(db_name, csv_path):

    # csv_path = "/Users/anguswatters/Desktop/s3_downloads/9d01169a86e24fb8867823a6fcd249a6_1705762724.csv"
    
    # os.dirpaths(csv_path)

    # get filename from path
    filename = os.path.basename(csv_path)
    dir_path = os.path.dirname(csv_path)
    
    # make a temporary filename
    output_filename = filename.replace(".csv", "_unique_ingredients.csv")
    output_path = os.path.join(dir_path, output_filename)

    print(f"CREATING UNIQUE INGREDIENTS...")

    # read in CSV into pandas dataframe
    df = pd.read_csv(csv_path)

    print(f"--> Calculating unique ingredients in memory...")

    # create unique ingredients dataframe
    unique_ingreds = create_unique_ingredients(df)
    
    print(f"--> Number of unique ingredients: {len(unique_ingreds)}")
    print(f"--> Saving unique ingredients CSV file to '{output_path}'...")

    # save unique ingredients dataframe to csv
    unique_ingreds[["ingredient", "count"]].to_csv(output_path, index=False)

    print(f"--> UPSERTING unique ingredients into database...")
    
    # upsert unique ingredients into database
    upsert_unique_ingredients_into_db(db_name, output_path, "unique_ingredients_table", "staging_unique_ingredients_table")

    print(f"--> Deleting local file {output_path}...")
    
    # Delete the local file
    subprocess.run(f"rm {output_path}", shell=True)

    print(f"----" * 5)
    print(f"UPSERT of unique ingredients ATTEMPT COMPLETE!")
    print(f"----" * 5)

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
            count = {target_table}.count + EXCLUDED.count  -- Increment count if ingredient exists
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
        else:
            try: 
                print(f"---" * 5)
                print(f"------ TRYING TO LOOK AT UPDATING COUNTS -------")
                print(f"---" * 5)
                # Parse the output to determine inserted and updated rows
                rows_affected = upsert_output.stdout.strip().split('\n')
                inserted_rows = [row.split('\t') for row in rows_affected if "INSERT 0 1" in row]
                updated_rows = [row.split('\t') for row in rows_affected if "UPDATE 1" in row]

                print(f"Inserted Rows: {inserted_rows}")
                print(f"Updated Rows: {updated_rows}")
                print(f"---" * 5)
            except Exception as e:
                print(f"Exception raised while parsing upsert output:\n{e}")

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
    # #########################
    # df = recipe_df
    # json_column = "ingredient_tags"

    # Example ingredient_tags column value:
    '{"ingredient_tags": ["cream", "lingonberry sauce", "fruit preserves", "egg whites", "salt", "sugar", "flour", "egg yolks", "vanilla extract", "sugar"]}'
    # #########################

    print(f"Generating unique ingredients from '{json_column}' column...")

    # Select just ingredients column
    df = df[[json_column]]

    print(f"Converting '{json_column}' column to dictionary...")
    # convert json dictionary column to dictionary and then list
    df[json_column] = df[json_column].apply(lambda row: json.loads(row)[json_column])
    # df["ingredients"] = df["ingredients"].apply(lambda row: json.loads(row)['ingredients'])

    print(f"Exploding '{json_column}' column...")
    # explode "ingredients" list column to make an individual row for each ingredients in each dish
    df = df.explode([json_column]).reset_index(drop=True)
    # df = df.explode(['ingredients']).reset_index(drop=True)

    print(f"Removing extra whitespaces...")
    # replace whitespace with single space
    df[json_column] = df[json_column].replace(r'\s+', ' ', regex=True)
    # df["ingredients"] = df["ingredients"].replace(r'\s+', ' ', regex=True)

    print(f"Setting all characters to lowercase...")
    # convert all characters in 'ingredients' to lowercase
    df[json_column] = df[json_column].str.lower()
    # df['ingredients'] = df['ingredients'].str.lower()

    print(f"Counting unique ingredients...")
    # CREATE FREQUENCY DATAFRAME
    # ingreds_df = df[["ingredients"]]
    freq_df = df[[json_column]].value_counts()
    # freq_df = df[["ingredients"]].value_counts()

    print(f"Making 'freq_df'")
    # convert series to dataframe
    freq_df = pd.DataFrame(freq_df)

    # reset index
    freq_df = freq_df.reset_index()

    print(f"Dropping duplicates...")
    # select unique ingredients
    unique_ingreds = df[[json_column]].drop_duplicates(subset=[json_column], keep='first')
    # unique_ingreds = df[["ingredients"]].drop_duplicates(subset=['ingredients'], keep='first')

    print(f"Merging counts with unique ingredients...")
    # merge counts with unique ingredients
    unique_ingreds = pd.merge(unique_ingreds, freq_df, on=json_column, how='left')
    # unique_ingreds = pd.merge(unique_ingreds, freq_df, on='ingredients', how='left')

    print(f"Fill NaN values with 0...")
    # replace NaN values with 0
    unique_ingreds['count'].fillna(0, inplace=True)

    print(f"Convert the 'float_column' to an integer...")
    # Convert the 'float_column' to an integer
    unique_ingreds['count'] = unique_ingreds['count'].astype(int)

    print(f"Sort unique ingredients by count in descending order...")
    # sort unique_ingreds by count in descending order
    unique_ingreds = unique_ingreds.sort_values(by='count', ascending=False)

    # add unique id for each ingredient
    unique_ingreds["ingredient_id"] = unique_ingreds.index

    print(f"Changing column names...")
    # rename json_column to "ingredient"
    unique_ingreds = unique_ingreds.rename(columns={json_column: "ingredient"})
    
    # reorder columns
    unique_ingreds = unique_ingreds[["ingredient_id", "ingredient", "count"]]
    # unique_ingreds = unique_ingreds[["ingredient_id", json_column, "count"]]

    # # save unique ingredients dataframe to csv
    # unique_ingreds[["ingredients_id", "ingredients", "count"]].to_csv('data/unique_ingredients.csv', index=False)

    return unique_ingreds

def make_unique_ingredients(input_csv_path, output_csv_path, json_column="ingredient_tags"):
    """Create unique ingredients dataset from a local CSV file.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path to the output CSV file.
        json_column (str): JSON column containing ingredient tags.

    Returns:
        list of dictionaries: Unique ingredients dataset.
    """
    #####################
    #####################
    
    # tmp = pd.read_csv('/Users/anguswatters/Downloads/9d01169a86e24fb8867823a6fcd249a6_1705762724.csv')
    # # tmp = pd.read_csv('/Users/anguswatters/Downloads/5dbe3e1610654706bd4da237da7be2bd_1705762730.csv')

    # # tmp
    # create_unique_ingredients(tmp)
    # len(create_unique_ingredients(tmp))
    # input_csv_path = '/Users/anguswatters/Downloads/9d01169a86e24fb8867823a6fcd249a6_1705762724.csv'
    # output_csv_path = '/Users/anguswatters/Desktop/s3_downloads/u_ingredients_test.csv'
    # json_column="ingredient_tags"

    #####################
    #####################

    print(f"Generating unique ingredients from '{json_column}' column...")

    # Read CSV file
    with open(input_csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)
    # len(data)
    # len(data[0])
    # data[0]
    
    # Initialize a defaultdict to store ingredient counts
    ingredient_counts = defaultdict(int)
    
    i = 0

    # Process each row in the CSV data
    for row in data:
        print(f"--" * 5)
        i += 1
        print(f"Processing row {i}...")
        print(f"row[json_column]: {row[json_column]}")
        # row
        # row[json_column]

        # Extract the list of ingredients from the JSON column
        ingredient_list = json.loads(row[json_column])[json_column]

        # Normalize and count each ingredient
        for ingredient in ingredient_list:
            print(f"Processing ingredient '{ingredient}'...")
            normalized_ingredient = ingredient.lower().strip()
            print(f"----> Normalized ingredient: '{normalized_ingredient}'")
            ingredient_counts[normalized_ingredient] += 1
        print(f"--" * 5)
        print(f"--" * 5)

    # Convert ingredient counts to a list of dictionaries
    unique_ingredients = [
        {"ingredient": ingredient, "count": count, "ingredient_id": index}
        for index, (ingredient, count) in enumerate(ingredient_counts.items())
    ]

    # Sort unique ingredients by count in descending order
    unique_ingredients.sort(key=lambda x: x["count"], reverse=True)

    # Save unique ingredients to CSV
    with open(output_csv_path, 'w', newline='') as output_csv:
        fieldnames = ["ingredient_id", "ingredient", "count"]
        writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_ingredients)

    print(f"Unique ingredients dataset saved to '{output_csv_path}'.")

    return unique_ingredients
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
# Primary logic that gets run within main() function
# - Download the object from S3, copy it into the database, and delete the local file
# - Upsert the new recipes CSV data into the database
# - Create unique ingredients dataset from new recipes CSV file (saved locally) and upsert all of the unique ingredients into the database
# - Delete the local files
def upsert_s3_data_into_db(client, s3_bucket, s3_object_key, local_file_path): 
    # Download the object from S3
    # msg_body = json.loads(msg["Body"])

    # s3_bucket = msg_body["Records"][0]["s3"]["bucket"]["name"]
    # s3_object_key = msg_body["Records"][0]["s3"]["object"]["key"]
    # local_file_path = f"s3_downloads/{s3_key_filename}"
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

    # print(f"===========================")
    # print(f"==== ATTEMPT to UPSERT (into recipe_table2) ====")
    # print(f"==== Trying to UPSERT {local_file_path} into 'recipe_table2' in database ====")
    # print(f"===========================")

    # # Try and execute the upsert script
    # # upsert_csv_into_db(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")
    # upsert_recipe_csv_into_db(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")

    # # execute_upsert_script(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")

    # print(f"----> Succesfully UPSERTED {local_file_path} into 'recipe_table2' database!")
    # print(f"=====" * 8)

    print(f"===========================")
    print(f"==== ATTEMPT to UPSERT (unique_ingredients) ====")
    print(f"==== Trying to UPSERT {local_file_path} into 'unique_ingredients' in database ====")
    print(f"===========================")

    # Try and execute the upsert script
    # upsert_csv_into_db(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")
    create_and_upsert_unique_ingredients_data(DB_NAME, local_file_path)

    # execute_upsert_script(DB_NAME, local_file_path, "recipe_table2", "staging_recipe_table2")

    print(f"----> Succesfully UPSERTED {local_file_path} into 'unique_ingredients' database!")
    
    
    print(f"=====" * 8)
    print(f"=====" * 8)

    ################### ALL GOOD TO GO ##############################
    print(f"Sleeping for 3 seconds...")

    time.sleep(5)

    print(f"Deleting local file {local_file_path}...")

    # Delete the local file
    subprocess.run(f"rm {local_file_path}", shell=True)

    return 

# Create a /copy command to copy CSV into a specified database table
def create_slash_copy_cmd(db_name, table_name, csv_path):
    copy_cols = "author, category, cook_time, cuisine, description, host, image, ingredient_tags, ingredients, instructions, prep_time, ratings, sorted_ingredient_tags, timestamp, title, total_time, url, yields"
    
    copy_command= f'\copy {table_name} ({copy_cols}) FROM \'{csv_path}\' DELIMITER \',\' CSV HEADER;'
    
    return copy_command


