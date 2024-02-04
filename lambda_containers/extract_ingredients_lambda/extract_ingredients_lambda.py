import json
import os
import boto3
import uuid
import time 
import re
import ast

# import datetime 
from datetime import datetime

# Set TRANSFORMERS_CACHE to /tmp
os.environ["TRANSFORMERS_CACHE"] = "/tmp"

import pandas as pd
import numpy as np 

import s3fs

# import model interface from Hugging Face model 
from food_extractor.food_model import FoodModel

# Credit: https://github.com/chambliss/foodbert.git
# Thank you for the model and heurtistics for extracting food ingredients from a list of ingredients! 

# # GitHub Repository: https://github.com/chambliss/foodbert/tree/master

# environment variables
OUTPUT_S3_BUCKET = os.environ.get('OUTPUT_S3_BUCKET')

# path to saved distilbert FoodModel from Hugging Face
model_path = './model/chambliss-distilbert-for-food-extraction'
# model_path = './extract_ingredients_lambda/model/chambliss-distilbert-for-food-extraction'

# Load the model from HuggingFace
model = FoodModel(model_path)
# model = FoodModel("chambliss/distilbert-for-food-extraction")

print(f"Succesfully loaded model from: {model_path}")
print(f"type(model): {type(model)}")

# S3 client
s3 = boto3.client('s3')

# # function to extract food ingredients from a list of ingredients using the FoodModel
def generate_tags(model, ingredient_list):

    food_tags = []

    input = " ... ".join(ingredient_list)

    model_output = model.extract_foods(input)

    for food in model_output[0]["Ingredient"]:
        food_tags.append(food['text'].lower())
        
    # return food_tags
    return json.dumps(food_tags)

def clean_scraped_data(df):
    
    # df = pd.read_csv(s3_path_string)
    # df["sorted_ingredient_tags"] = '[]' 
    # df.drop(columns=['uid'], inplace=True)

    # list of columns to keep
    cols_to_keep = ["author", "category", "cook_time", "cuisine", 
                           "description", "host", "image", "ingredient_tags", "ingredients", 
                           "instructions", "prep_time", "ratings", 
                           "sorted_ingredient_tags", "timestamp", "title", "total_time", 
                           "url", "yields"]
    
    # drop any columns that are not in the cols_to_keep list
    df = df[cols_to_keep]

    # list of columns that will end up as jsonb columns in postgres database
    jsonb_columns = ['category', 'ingredients', 'instructions', 'cuisine', 
                     'ingredient_tags', 'sorted_ingredient_tags']
    # jsonb_columns = ['category', 'ingredients', 'instructions', 'cuisine', 'ingredient_tags']

    # list of columns that will end up as text columns in postgres database
    text_columns = ['title', 'host', 'yields', 'image', 'author', 'description', 'url']
    # text_columns = ['title', 'host', 'yields', 'image', 'author', 'description', 'uid', 'url']

    # list of columns that will end up as integer columns in postgres database
    integer_columns = ['timestamp', 'total_time', 'cook_time', 'prep_time']

    # list of columns that will end up as float columns in postgres database
    float_columns = ['ratings']
    
    print(f"Convert jsonb columns to lists...")

    # loop over json columns and use "ast" to convert stringified list into a list for all jsonb columns
    for column in jsonb_columns:
        df[column] = df[column].apply(ast.literal_eval)

    print(f"Strip any trailing/leading whitespaces...")

    # loop through jsonb columns and strip away any trailing/leading whitespaces
    for column in jsonb_columns:
        df[column] = df[column].apply(lambda x: [s.strip() for s in x])
    
    # df.ingredients
    # df.ingredient_tags
    # df.ingredient_tags.values.tolist()[0]
    # # loop through jsonb columns and remove any non alpha numerics and strip away any trailing/leading whitespaces
    # for column in jsonb_columns:
    #     df[column] = df[column].apply(lambda x: [re.sub('[^A-Za-z ]', '', s).strip() for s in x])
    
    print(f"Removing any unicode values in list columns...")

    # loop through jsonb columns and santize list columns by removing unicode values
    for column in jsonb_columns:
        df[column] = df[column].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
    
    # df.ingredients
    # df.ingredient_tags
    # df.ingredient_tags.values.tolist()[0]

    print(f"Coercing integer columns to Int64 and replacing missing/NaN values with 0...")

    # coerce integer columns to Int64 and replace missing/NaN values with 0
    for column in integer_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64').fillna(0)

    print(f"Coercing float columns to float64 and replacing missing/NaN values with 0...")
    # loop through float_columns coerce all ratings values to float64 and replace missing/NaN values with 0
    for column in float_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('float64').fillna(0)

    # sort by lowercased values
    def lowercase_sort(lst):
        return sorted(lst, key=lambda x: x.lower()) 
    
    print(f"Sort the ingredients in each recipe...")
    # sort the ingredient_tags and make a new sorted_ingredient_tags column
    df = df.assign(sorted_ingredient_tags = lambda x: (x["ingredient_tags"].apply(lowercase_sort)))

    # convert a dictionary column to json  function:
    def dict2json(dictionary):
        return json.dumps(dictionary, ensure_ascii=False)
    
    print(f"Convert jsonb columns to dictionaries...")
    # loop through jsonb columns and convert list columns into dictonary columns
    for column in jsonb_columns:
        df[column] = df.apply(lambda row: {column:row[column]}, axis=1)

    print(f"Convert dictionary columns to json columns...")
    # loop thorugh jsonb columns and convert dictionary columns to json columns
    for column in jsonb_columns:
        df[column] = df[column].map(dict2json)
    
    print(f"Arranging columns in alphabetical order...")
    # Sort columns by alphabetical order
    df = df.sort_index(axis=1)

    print(f"Checking all needed columns are present...")
    # make a set of the dataframe columns to make sure all columns are present
    df_cols = set(df.columns)

    # final output columns to make sure all columns are present
    output_columns = set(cols_to_keep)
    
    # TODO: RAISE an error here for missing columns and process the error in the lambda_handler
    # TODO: If all output columns are not present, then the data may need to be set aside and checked out down the road
    # check if all columns are present
    if output_columns != df_cols:
        missing_cols = output_columns.difference(df_cols)
        print(f"MISSING COLUMNS in df: {missing_cols}")
        print(f"Adding missing columns to df...")
        add_missing_columns(df, missing_cols)
    else:
        print(f"No missing columns in df")

    # manually select and order columns for final output in alphabetical order
    df = df[['author', 'category', 'cook_time', 'cuisine', 'description', 'host',
            'image', 'ingredient_tags', 'ingredients', 'instructions', 'prep_time',
            'ratings', 'sorted_ingredient_tags', 'timestamp', 'title', 'total_time', 'url',
            'yields']]
    
    print(f"Fill any NaN with default values...")

    # fill any NaN with default values for each column
    df = fillna_default_vals(df)

    # output row and column count
    print(f"number of rows: {df.shape[0]}")
    print(f"number of cols: {df.shape[1]}")

    print(f"----> SUCCESS, data cleaning complete!")

    return df

# Add any missing columns in pandas dataframe with the correct type and default values, 
# then reorder the columns to be alphabetical (all of this is done IN PLACE)
def add_missing_columns(df, missing_columns):
    # create a dictionary of the keys and their data types
    keys_to_type_map = {
        "host": object,
        "title": object,
        "category": object,
        "total_time": np.int64,
        "cook_time": np.int64,
        "prep_time": np.int64,
        "yields": object,
        "image": object,
        "ingredients": object,
        "instructions": object,
        "ratings": np.float64,
        "author": object,
        "cuisine": object,
        "description": object,
        # "uid": str,
        "url": object,
        "ingredient_tags": object,
        "sorted_ingredient_tags": object,
        "timestamp": np.int64
        }
    
    # create a dictionary of the keys and their data types
    default_vals_map = {
        "host": "",
        "title": "",
        "category": '{"category": [""]}',
        "total_time": 0,
        "cook_time": 0,
        "prep_time": 0,
        "yields": "",
        "image": "",
        "ingredients": '{"ingredients": [""]}',
        "instructions": '{"instructions": [""]}',
        "ratings": 0,
        "author": "",
        "cuisine": '{"cuisine": [""]}',
        "description": "",
        "url": "",
        "ingredient_tags": '{"ingredient_tags": [""]}',
        "sorted_ingredient_tags": '{"sorted_ingredient_tags": [""]}',
        "timestamp": 0
        }

    # Iterate over missing columns and add them to the DataFrame with appropriate data type
    for column in missing_columns:
        

        print(f"Adding column: {column}")
        try:

            data_type = keys_to_type_map.get(column, object)  # default to object type if not found in the map
            print(f"data_type: {data_type}")
            # default_value = default_vals_map.get(column, "")  # default to empty string if not found in the map
            # print(f"default_value: {default_value}")

            # Add a new column with the correct data type and default value
            df[column] = pd.Series(dtype=data_type)
            # df[column] = pd.Series([default_value for i in range(len(df))], dtype=data_type)
        except Exception as e:
            print(f"Error adding column: {e}")
            print(f"Skipping column: {column}")

    # Sort columns by alphabetical order
    df.sort_index(axis=1, inplace=True)

# create a function to use pandas fill na to fill all missing values in dataframe with specified default values from default value map
def fillna_default_vals(df):

    # create a dictionary of the keys and their data types
    default_vals_map = {
        "host": "",
        "title": "",
        "category": '{"category": [""]}',
        "total_time": 0,
        "cook_time": 0,
        "prep_time": 0,
        "yields": "",
        "image": "",
        "ingredients": '{"ingredients": [""]}',
        "instructions": '{"instructions": [""]}',
        "ratings": 0,
        "author": "",
        "cuisine": '{"cuisine": [""]}',
        "description": "",
        "url": "",
        "ingredient_tags": '{"ingredient_tags": [""]}',
        "sorted_ingredient_tags": '{"sorted_ingredient_tags": [""]}',
        "timestamp": 0
        }
    
    df = df.fillna(value=default_vals_map, inplace=False)

    return df

# # Create an example DataFrame
# data = {
#     "author": [np.nan, "Bob", "Charlie"],
#     "title": ["Recipe 1", "Recipe 2", "Recipe 3"],
#     "category": ["Dessert", "Main Dish", "Appetizer"],
#     "ingredient_tags": [np.nan, '{"ingredient_tags": [""]}',  '{"ingredient_tags": [""]}'],
#     "cook_time": [30, 45, 20],
# }

# df2 = pd.DataFrame(data)

# # Define the output_columns set
# output_columns = set(["author", "category", "cook_time", "cuisine", "description", "host", "image",
#                       "ingredient_tags", "ingredients", "instructions", "prep_time", "ratings",
#                       "sorted_ingredient_tags", "title", "total_time", "url", "yields"])

# # Check if all columns are present
# df_cols = set(df2.columns)
# if output_columns != df_cols:
#     missing_cols = output_columns.difference(df_cols)
#     print(f"Missing columns in df: {missing_cols}")
#     print(f"Adding missing columns to df")
#     add_missing_columns(df2, missing_cols)
# df2.ingredient_tags
# fillna_default_vals(df2)

def extract_ingredients_from_s3_event(message):
    # example_json = {
    #     'uid': 'spanishsquash_906928', 
    #     'url': 'https://www.allrecipes.com/recipe/73794/spanish-squash/',
    #     'ingredients': ['1 pound ground beef', '1 tablespoon vegetable oil', '3 medium yellow squash, sliced', '1 small yellow onion, sliced', '1 (14.5 ounce) can diced tomatoes, drained', '0.5 cup water', '1 teaspoon chili powder', '0.25 teaspoon cumin', '1 dash garlic powder', 'salt and pepper to taste'] 
    #     }
    # batch_events = [example_json for i in range(4)]
    # batch_events = [event for i in range(4)]
    # batch_ingredients = [example_json["ingredients"] for i in range(5)]

    # print(f"model: {model}")
    print(f"=====================")
    print(f'---->\n Value of message: {message}')
    print(f"=====================")

    # s3_event = message["body"]
    s3_event = json.loads(message["body"])
    # s3_event = json.loads(message)["body"]

    print(f"=====================")
    print(f'---->\n Value of s3_event: {s3_event}')
    print(f"=====================")

    # # Extract the S3 bucket and the filename from the S3 event notification JSON object
    S3_BUCKET    = s3_event['Records'][0]['s3']['bucket']['name']
    S3_FILE_NAME = s3_event['Records'][0]['s3']['object']['key']

    print(f"- S3_BUCKET: {S3_BUCKET}")
    print(f"- S3_FILE_NAME: {S3_FILE_NAME}")

    print(f"Gathering JSON file from S3...")

    # get the object from S3
    s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_NAME)

    # read the JSON file into a dictionary
    s3_json = json.load(s3_obj["Body"])

    print(f"s3_json: {s3_json}")

    # key of ingredients list in JSON object
    ingredients_key = "ingredients"
    # ingredients_key = "scraped_ingredients"
    
    # extract food tags from ingredients list using FoodModel
    food_tags = generate_tags(model, s3_json[ingredients_key])

    print(f"--> food_tags: {food_tags}")
    
    # Add FoodModel tags to JSON object
    s3_json["ingredient_tags"] = food_tags

    try:
        s3_json = sanitize_json(s3_json)
    except Exception as e:
        print(f"Error sanitizing json: {e}")
        print(f"Returning s3_json without sanitization")
        return s3_json
    # # "scraped" in i.split("_")
    # keep_keys = [i for i in s3_json.keys() if i == "uid" or  "scraped" in i.split("_")]
    # keep_keys.insert(1, "url")

    # final_json = {}

    # for i in keep_keys:
    #     print(f"i: {i}")
    #     print(f"s3_json[i]: {s3_json[i]}")
    #     if keep_keys == "url":
    #         final_json[i] = s3_json["scraped_canonical_url"]
    #     else:
    #         # add the next key to the list of keys to keep
    #         final_json[i] = s3_json[i]

    # # remove the string "scraped_" from any keys in the final_json
    # final_json = {key.replace("scraped_", ""): value for key, value in final_json.items()}

    return s3_json
    

# santitize_json function to complete
def sanitize_json(json_obj):
    # create a function that ensures each output json (python dictionary) has the same keys, 
    # if any keys are missing, then insert an appropriate missing value)

    # create a list of all the keys that should be in each json object
    keys_to_keep = [
        "host", "title", "category", "total_time", "cook_time", "prep_time",
        "yields", "image", "ingredients", "instructions", "ratings",
        "author", "cuisine", "description", 
        "uid", "url", "ingredient_tags", "timestamp" # keys that are added and do NOT come from the recipe scraper
        ]
    
    # create a dictionary of the keys and their data types
    keys_to_type_map = {
        "host": str,
        "title": str,
        "category": list,
        "total_time": int,
        "cook_time": int,
        "prep_time": int,
        "yields": str,
        "image": str,
        "ingredients": list,
        "instructions": list,
        "ratings": int,
        "author": str,
        "cuisine": list,
        "description": str,
        "uid": str,
        "url": str,
        "ingredient_tags": list,
        "timestamp": int
        }
    
    # iterate over each key and add it with an appropriate empty value if missing
    for key in keys_to_keep:
        # print(f"key: {key}")
        # check if key is in json object
        if key not in json_obj or json_obj[key] is None:
            # print(f"==== '{key}' not in json_obj or is None ====")
            # print(f"---> Adding key: {key} to json_obj")

            # add key with an empty value based on the data type
            default_value = (
                0 if keys_to_type_map[key] == int else
                [] if keys_to_type_map[key] == list else
                ""  # assuming all other cases are strings
            )

            # if key is "timestamp", set to current time
            if key == "timestamp":
                default_value = int(time.time())

            json_obj[key] = default_value
        else:
            # print(f"==== '{key}' in json_obj ====")
            # print(f"---> json_obj[key]: {json_obj[key]}")
            # print(f"---> type(json_obj[key]): {type(json_obj[key])}")

            # coerce the value to the expected type if needed
            expected_type = keys_to_type_map[key]
            current_type = type(json_obj[key])
            # print(f"---> expected_type: {expected_type}")
            # print(f"---> current_type: {current_type}")

            if current_type != expected_type:
                # print(f"current_type != expected_type")
                # print(f"Trying to coerce json_obj[key] to expected_type {expected_type}")
                try:
                    # try to coerce the value to the expected type
                    if expected_type == list:
                        # if expected type is list and value is a string, put it in a list
                        json_obj[key] = [json_obj[key]]
                    else:
                        json_obj[key] = expected_type(json_obj[key])
                except ValueError:
                    # handle the case where coercion is not possible, set to default value
                    json_obj[key] = (
                        0 if expected_type == int else
                        [] if expected_type == list else
                        ""  # assuming all other cases are strings
                    )
                    
                    # if key is "timestamp", set to current time
                    if key == "timestamp":
                        json_obj[key] = int(time.time())
        #         print(f"json_obj[key] after coercion: {json_obj[key]}")
        #         print(f"json_obj[key] type after coercion: {type(json_obj[key])}")
        # print(f"=====" * 5)

    # Remove keys that are not in keys_to_keep
    json_obj = {key: json_obj[key] for key in keys_to_keep if key in json_obj}

    return json_obj


def get_csv_from_s3(message):

    print(f'---->\n Value of message: {message}')

    # s3_event = message["body"]
    s3_event = json.loads(message["body"])
    # s3_event = json.loads(message)["body"]

    print(f'---->\n Value of s3_event: {s3_event}')


    # # Extract the S3 bucket and the filename from the S3 event notification JSON object
    S3_BUCKET    = s3_event['Records'][0]['s3']['bucket']['name']
    S3_FILE_NAME = s3_event['Records'][0]['s3']['object']['key']

    print(f"- S3_BUCKET: {S3_BUCKET}")
    print(f"- S3_FILE_NAME: {S3_FILE_NAME}")

    print(f"Gathering CSV file from S3...")
    
    try:

        # get the object from S3
        s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_NAME)
    except Exception as e:
        print(f"Error getting CSV file from S3: {e}")
        # Handle the exception here, or raise a specific error
        raise Exception(f"Error processing element: {e}")

    # read the CSV file into a pandas dataframe
    csv_df = pd.read_csv(s3_obj["Body"])
    
    print(f"csv_df: {csv_df}")
    print(f"csv_df.shape: {csv_df.shape}")

    return csv_df

# Create a list of the [year, month, day] when the function is run (YYYY, MM, DD)
# Use the [year, month, day] in prefix of the uploaded S3 object
def get_event_date():

    # Use the current date and time as the default
    event_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Parse the eventTime string into a datetime object
    parsed_event_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Extract month, day, and year
    month = parsed_event_time.strftime("%m")
    day   = parsed_event_time.strftime("%d")
    year  = str(parsed_event_time.year)

    # create a date_key string
    print(f"Year: {year}, Month: {month}, Day: {day}")

    return [year, month, day]

# lambda handler function
def extract_ingredients_lambda(event, context):

    message_count = 0
    
    batch_item_failures = []
    sqs_batch_response = {}
    
    output_data = []

    for message in event["Records"]:
    # for message in scraped_list:
        message_count += 1
        print(f"==== PROCESSING MESSAGE: {message_count} ====")
        # print(f"message {message_count}: {message}")
        try:

            s3_csv = get_csv_from_s3(message)
            
            print(f"s3_csv.shape: {s3_csv.shape}")

            output_data.append(s3_csv)

            # output_json = extract_ingredients_from_s3_event(message)
            # output_data.append(output_json)

        except Exception as e:
            print(f"Exception raised from messageId {message['messageId']}\n: {e}")
            batch_item_failures.append({"itemIdentifier": message['messageId']})


    print(f"Concating output_data...")
    print(f"len(output_data): {len(output_data)}")

    # Convert list of dictionaries to pandas dataframe
    df = pd.concat(output_data)

    # df.drop(columns=['uid'], inplace=True)
    # df["sorted_ingredient_tags"] = "['']" 

    # # Convert list of dictionaries to pandas dataframe
    # df = pd.DataFrame(output_data)

    print(f"df.shape: {df.shape}")
    print(f"df: {df}")

    print(f"Applying FoodModel to generate ingredient tags...")
    
    # df['ingredients'].values.tolist()[0]

    # # # convert the stringified list into a list for the ingredients, NER, and directions columns
    # df['ingredients'] = df['ingredients'].apply(ast.literal_eval)
    
    # # Add ingredient tags to dataframe
    # df["ingredient_tags"] = df["ingredients"].apply(lambda x: generate_tags(model, x))

    # Add ingredient tags to dataframe using HuggingFace BERT FoodModel
    df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: generate_tags(model, x))

    print(f"---- Cleaning scraped data ----")

    # clean the scraped dataframe
    df = clean_scraped_data(df)
    
    # get the current year, month, and day
    year, month, day = get_event_date()

    # generate a random UUID to add to the OUTPUT_S3_OBJECT_NAME
    unique_id = f"{uuid.uuid4().hex}"

    # Use uuid.uuid4() and current timestamp to create a unique filename
    csv_key = f"{unique_id}_{int(time.time())}.csv"

    # create the S3 filename
    OUTPUT_S3_FILENAME = f"s3://{OUTPUT_S3_BUCKET}/{year}/{month}/{day}/{csv_key}"
    # OUTPUT_S3_FILENAME = f"s3://{OUTPUT_S3_BUCKET}/{csv_key}"

    print(f"Saving dataframe to S3:\n - OUTPUT_S3_FILENAME: '{OUTPUT_S3_FILENAME}'")

    # save the dataframe to S3
    df.to_csv(OUTPUT_S3_FILENAME, index=False)

    sqs_batch_response["batchItemFailures"] = batch_item_failures

    print(f"sqs_batch_response: {sqs_batch_response}")

    return sqs_batch_response

# s3_events = [{
#   "Records": [
#     {
#       "eventVersion": "2.1",
#       "eventSource": "aws:s3",
#       "awsRegion": "us-east-2",
#       "eventTime": "2019-09-03T19:37:27.192Z",
#       "eventName": "ObjectCreated:Put",
#       "userIdentity": {
#         "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
#       },
#       "requestParameters": {
#         "sourceIPAddress": "205.255.255.255"
#       },
#       "responseElements": {
#         "x-amz-request-id": "D82B88E5F771F645",
#         "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
#       },
#       "s3": {
#         "s3SchemaVersion": "1.0",
#         "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
#         "bucket": {
#        # "name": "XXX-staging-bucket",
#           "ownerIdentity": {
#             "principalId": "A3I5XTEXAMAI3E"
#           },
#           "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
#         },
#         "object": {
#           "key": "stage_1002331_www_food_com_13eba7aff036423fa7c7e19b62180aaf.json",
#           "size": 1305107,
#           "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
#           "sequencer": "0C0F6F405D6ED209E1"
#         }
#       }
#     }
#   ]
# },
# {
#   "Records": [
#     {
#       "eventVersion": "2.1",
#       "eventSource": "aws:s3",
#       "awsRegion": "us-east-2",
#       "eventTime": "2019-09-03T19:37:27.192Z",
#       "eventName": "ObjectCreated:Put",
#       "userIdentity": {
#         "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
#       },
#       "requestParameters": {
#         "sourceIPAddress": "205.255.255.255"
#       },
#       "responseElements": {
#         "x-amz-request-id": "D82B88E5F771F645",
#         "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
#       },
#       "s3": {
#         "s3SchemaVersion": "1.0",
#         "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
#         "bucket": {
#           "name": "XXX-staging-bucket",
#           "ownerIdentity": {
#             "principalId": "A3I5XTEXAMAI3E"
#           },
#           "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
#         },
#         "object": {
#           "key": "stage_1000728_www_food_com_58710ba04909411aad0ce392b91541a5.json",
#           "size": 1305107,
#           "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
#           "sequencer": "0C0F6F405D6ED209E1"
#         }
#       }
#     }
#   ]
# }, {
#   "Records": [
#     {
#       "eventVersion": "2.1",
#       "eventSource": "aws:s3",
#       "awsRegion": "us-east-2",
#       "eventTime": "2019-09-03T19:37:27.192Z",
#       "eventName": "ObjectCreated:Put",
#       "userIdentity": {
#         "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
#       },
#       "requestParameters": {
#         "sourceIPAddress": "205.255.255.255"
#       },
#       "responseElements": {
#         "x-amz-request-id": "D82B88E5F771F645",
#         "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
#       },
#       "s3": {
#         "s3SchemaVersion": "1.0",
#         "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
#         "bucket": {
#           "name": "XXXX-bucket",
#           "ownerIdentity": {
#             "principalId": "A3I5XTEXAMAI3E"
#           },
#           "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
#         },
#         "object": {
#           "key": "stage_1002258_www_food_com_82babaa83b20495691d5304f7aa45266.json",
#           "size": 1305107,
#           "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
#           "sequencer": "0C0F6F405D6ED209E1"
#         }
#       }
#     }
#   ]
# }]

# event_list = []

# for i in s3_events:
#     event_list.append(
#         json.dumps({
#             "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
#             "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
#             "body": i,
#             "attributes": {
#                 "ApproximateReceiveCount": "1",
#                 "SentTimestamp": "1545082649183",
#                 "SenderId": "AIDAIENQZJOLO23YVJ4VO",
#                 "ApproximateFirstReceiveTimestamp": "1545082649185"
#             },
#             "messageAttributes": {},
#             "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
#             "eventSource": "aws:sqs",
#             "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
#             "awsRegion": "us-east-2"
#         })
#         )
    
# event = {}
# event["Records"] = event_list

# event["Records"][0]
# json.loads(event["Records"][0])


# scraped_list = [
#     {'uid': 'test_uid', 'url': 'https://www.food.com/recipe/lenten-lentils-oaxacan-style-85328', 
#      'author': 'EdsGirlAngie', 
#      'canonical_url': 'https://www.food.com/recipe/lenten-lentils-oaxacan-style-85328', 
#      'category': 'One Dish Meal', 
#      'host':
#      'food.com', 
#      'image': 'https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/recipes/85/32/8/picmNxxBC.jpg', 
#      'ingredient_groups': [{'ingredients': ['3/4 cup dried lentils', '4 cups water', '2 cloves garlic, halved', "1/2 white onion, halved (so it's in quarters)", '1 tablespoon vegetable oil', '2 cloves garlic, minced', '1/2 white onion, chopped', '1 plantain, peeled and chopped', '10 ounces cans unsweetened pineapple slices, cut into chunks', '2 medium ripe tomatoes, peeled,seeded and chopped', '1/4 teaspoon clove', '1/2 teaspoon allspice'], 'purpose': None}], 'ingredients': ['3/4 cup dried lentils', '4 cups water', '2 cloves garlic, halved', "1/2 white onion, halved (so it's in quarters)", '1 tablespoon vegetable oil', '2 cloves garlic, minced', '1/2 white onion, chopped', '1 plantain, peeled and chopped', '10 ounces cans unsweetened pineapple slices, cut into chunks', '2 medium ripe tomatoes, peeled,seeded and chopped', '1/4 teaspoon clove', '1/2 teaspoon allspice'], 'instructions': "Bring lentils and water to a boil, with 2 halved garlic cloves and 1/2 white onion.\nReduce heat, then cover and simmer over low heat about 20 minutes or until lentils are tender but not mushy.\nDrain and reserve lentil cooking liquid.\nAt this point, I like to fish out the garlic halves but leave the onion, which breaks down in the lentils.\nSeason with salt.\nHeat oil in large saucepan and saute chopped white onion and the 2 minced garlic cloves until onion is soft.\nAdd plantain, pineapple and tomatoes; cook until plantain is soft, anywhere from 15 to 25 minutes.\nAdd lentils and some reserved lentil cooking liquid.\nContinue cooking until mixture thickens a little; add more cooking liquid or even some vegetable or chicken broth if necessary so lentils aren't dry.\nServe garnished with fried plantain slices.", 'instructions_list': ['Bring lentils and water to a boil, with 2 halved garlic cloves and 1/2 white onion.', 'Reduce heat, then cover and simmer over low heat about 20 minutes or until lentils are tender but not mushy.', 'Drain and reserve lentil cooking liquid.', 'At this point, I like to fish out the garlic halves but leave the onion, which breaks down in the lentils.', 'Season with salt.', 'Heat oil in large saucepan and saute chopped white onion and the 2 minced garlic cloves until onion is soft.', 'Add plantain, pineapple and tomatoes; cook until plantain is soft, anywhere from 15 to 25 minutes.', 'Add lentils and some reserved lentil cooking liquid.', "Continue cooking until mixture thickens a little; add more cooking liquid or even some vegetable or chicken broth if necessary so lentils aren't dry.", 'Serve garnished with fried plantain slices.'], 'language': 'en', 'nutrients': {'calories': '277.4', 'fatContent': '4.2', 'saturatedFatContent': '0.6', 'cholesterolContent': '0', 'sodiumContent': '17', 'carbohydrateContent': '52.1', 'fiberContent': '14.4', 'sugarContent': '17.8', 'proteinContent': '11.3'}, 'ratings': 5.0, 'site_name': None, 'title': 'Lenten Lentils, Oaxacan-Style', 'total_time': 75, 'yields': '4 servings'}, {'uid': 'test_uid2', 'url': 'https://www.food.com/recipe/mamma-mia-fresh-italian-lasagne-411585', 
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            'author': 'The Spice Guru', 
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            'canonical_url': 'https://www.food.com/recipe/mamma-mia-fresh-italian-lasagne-411585', 
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            'category': 'European', 'host': 'food.com', 'image': 'https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/recipes/41/15/85/picSMZSZ9.jpg', 
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         'ingredient_groups': [{'ingredients': ['1 tablespoon olive oil', '1 medium chopped onion', '8 ounces thinly sliced fresh mushrooms', '2/3 cup minced fresh basil leaf', '2 -3 tablespoons minced fresh garlic', '3 tablespoons minced fresh Italian parsley', '2 tablespoons minced fresh oregano leaves', '1 teaspoon minced fresh rosemary leaf', '3 1/4 cups blanched diced fresh roma tomatoes (cored and skins removed, or one 28 oz can diced tomatoes)',
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 '3 1/4 cups blanched pureed fresh roma tomatoes (cored and skins removed, or one 28 oz can tomato sauce)', '1/4 cup olive oil', '2 -3 teaspoons ground fennel (may be ground in clean coffee grinder)', '1/4 cup chianti wine or 1/4 cup dry red wine', '2 teaspoons fine sea salt (to fresh tomato sauce only)', '1/4 teaspoon freshly grated lemon zest', '1/4 teaspoon freshly grated nutmeg', '1/4 teaspoon fresh ground black pepper', '1/4 teaspoon red pepper flakes', '1/4 cup freshly grated parmesan cheese', 'sugar or light corn syrup, to balance acidity', '1 cup semolina flour', '1/2 cup all-purpose flour', '3/8 teaspoon fine sea salt', '3 beaten eggs', '1 tablespoon olive oil', '2 tablespoons olive oil', '1 -2 fresh garlic clove, pressed', '3 cups whole milk ricotta cheese (Precious brand)', '1 large egg', '2/3 cup freshly grated parmesan cheese', '1/4 cup cream', '1/4 teaspoon freshly grated lemon zest', '1/4 teaspoon freshly grated nutmeg', '1/4 teaspoon fine sea salt', '1/4 teaspoon fresh ground white pepper', '1 small clove fresh mashed garlic', '1 cup finely chopped fresh Baby Spinach', '2 tablespoons minced fresh basil leaves (stems removed)', '16 ounces shredded fresh mozzarella cheese (or 16 oz Sargento shredded Italian cheese blend)', '1/4 cup freshly grated parmesan cheese', '1 tablespoon freshly grated parmesan cheese', '2 teaspoons seasoned Italian breadcrumbs (optional)', '1 teaspoon finely minced fresh Italian parsley'], 'purpose': None}], 'ingredients': ['1 tablespoon olive oil', '1 medium chopped onion', '8 ounces thinly sliced fresh mushrooms', '2/3 cup minced fresh basil leaf', '2 -3 tablespoons minced fresh garlic', '3 tablespoons minced fresh Italian parsley', '2 tablespoons minced fresh oregano leaves', '1 teaspoon minced fresh rosemary leaf', '3 1/4 cups blanched diced fresh roma tomatoes (cored and skins removed, or one 28 oz can diced tomatoes)', '3 1/4 cups blanched pureed fresh roma tomatoes (cored and skins removed, or one 28 oz can tomato sauce)', '1/4 cup olive oil', '2 -3 teaspoons ground fennel (may be ground in clean coffee grinder)', '1/4 cup chianti wine or 1/4 cup dry red wine', '2 teaspoons fine sea salt (to fresh tomato sauce only)', '1/4 teaspoon freshly grated lemon zest', '1/4 teaspoon freshly grated nutmeg', '1/4 teaspoon fresh ground black pepper', '1/4 teaspoon red pepper flakes', '1/4 cup freshly grated parmesan cheese', 'sugar or light corn syrup, to balance acidity', '1 cup semolina flour', '1/2 cup all-purpose flour', '3/8 teaspoon fine sea salt', '3 beaten eggs', '1 tablespoon olive oil', '2 tablespoons olive oil', '1 -2 fresh garlic clove, pressed', '3 cups whole milk ricotta cheese (Precious brand)', '1 large egg', '2/3 cup freshly grated parmesan cheese', '1/4 cup cream', '1/4 teaspoon freshly grated lemon zest', '1/4 teaspoon freshly grated nutmeg', '1/4 teaspoon fine sea salt', '1/4 teaspoon fresh ground white pepper', '1 small clove fresh mashed garlic', '1 cup finely chopped fresh Baby Spinach', '2 tablespoons minced fresh basil leaves (stems removed)', '16 ounces shredded fresh mozzarella cheese (or 16 oz Sargento shredded Italian cheese blend)', '1/4 cup freshly grated parmesan cheese', '1 tablespoon freshly grated parmesan cheese', '2 teaspoons seasoned Italian breadcrumbs (optional)', '1 teaspoon finely minced fresh Italian parsley'], 'instructions': 'PREP vegetables and herbs needed for the SAUTE FOR FRESH ITALIAN SAUCE (1 medium chopped onion, 8 ounces thinly sliced fresh mushrooms, 2/3 cup minced fresh basil leaves (reserving 1 tablespoon to refresh flavor later), 2-3 tablespoons minced fresh garlic, 3 tablespoons minced fresh Italian parsley, 2 tablespoons minced fresh oregano leaves, and 1 teaspoon minced fresh rosemary leaves); SAUTE in a large saucepan or pot in 1 tablespoon olive oil, between medium-low and medium heat until softened, about 7 minutes.\nBRING 4 quarts unsalted water to boiling; CAREFULLY lower Roma tomatoes needed for recipe on a large spoon into boiling water; BLANCH until skins start to crack; REMOVE tomatoes and place into a colander; RINSE tomatoes under running cold water to remove skins; PUREE enough tomatoes to yield 3 1/4 cups; DICE remaining tomatoes to yield 3 1/4 cups; ADD both pureed and diced tomatoes to the saute mixture, along with 1/4 cup olive oil, 2-3 teaspoons ground fennel, 1/4 cup dry red wine, 2 teaspoons fine sea salt (if using fresh tomatoes), 1/4 teaspoon freshly grated lemon zest, 1/4 teaspoon freshly grated nutmeg, 1/4 teaspoon fresh ground black pepper and 1/4 teaspoon red pepper flakes; STIR in enough sugar or light corn syrup into SAUCE to balance acidity; RAISE HEAT to HIGH, stirring constantly until mixture begins to boil; REDUCE heat to MEDIUM-LOW, then SIMMER the sauce uncovered for 1 hour or slightly longer, stirring occasionally; REMOVE the SAUCE from heat; STIR in 1/4 cup freshly grated parmesan cheese and 1 tablespoon finely minced fresh basil leaves (to refresh flavor); SEASON to taste with fine sea salt if necessary.\nIF PREPARING FRESH LASAGNE PASTA: While sauce is simmering: BEAT 3 eggs with 1 tablespoon olive oil gently in a medium bowl using a fork; into the large bowl of food processor MEASURE 1 cup semolina flour, 1/2 cup all-purpose flour and 3/8 teaspoon fine sea salt; PROCESS in food processor at least 30 seconds; with processor still running, very slowly POUR beaten eggs into feeder tube until all of the beaten eggs have been added; continue to PROCESS until dough becomes very thick and consistently blended (or when it forms a ball); REMOVE ball of dough from processor; WRAP dough tightly with plastic wrap; LET dough to rest at room temperature for 30 minutes. PLACE dough on a smooth clean surface dusted with semolina flour; ROLL out dough to 1/4 inch thick, SPRINKLE with semolina flour and repeat process until dough has a smooth, soft texture and with a balanced moisture level (not overly moist or dry); ROLL dough using a pasta machine (recommended), or a rolling pin to a 1/8 inch thickness, dusting very lightly with semolina flour if necessary, to prevent sticking; cut noodle dough into 2-3 inch width strips, with a 12" length; pasta does not need to be boiled first.\nIF USING PACKAGED LASAGNE PASTA: MEASURE exactly 4 quarts of water (16 cups) into a large pot of water; BRING water to a full rolling boil; ADD 4 teasppoons kosher salt, then quickly but carefully add 9-12 pasta strips; COOK pasta until just tender (al dente), about 7 to 8 minutes; DRAIN lasagne noodles immediately in a large colander; REMOVE pasta individually using tongs and HANG pasta in (and over), the edges of the large pot and the colander to STRAIGHTEN, so that none of the noodles are touching; ALLOW to cool slightly.\nPREPARE the PASTA BASTE by mixing 2 tablespoons olive oil with 1-2 cloves freshly pressed garlic (using a garlic press or mincing finely); BASTE lasagne noodles evenly on both sides in a 13 x 9 baking dish; REMOVE noodles and place aside.\nWHIP the following ingredients of the FRESH SPINACH AND CHEESE FILLING in a large bowl, using an electric mixer: 3 cups whole milk ricotta cheese (Precious brand), 1 large egg, 2/3 cup freshly grated parmesan cheese, 1/4 cup cream, 1/4 teaspoon freshly grated lemon zest, 1/4 teaspoon freshly grated nutmeg, 1/4 teaspoon fine sea salt, 1/4 teaspoon freshly ground white pepper, and 1 small clove fresh mashed garlic (use a garlic press); FOLD in 1 cup finely chopped fresh spinach leaves and 2 tablespoons minced fresh basil leaves (stems removed), until mixture is thoroughly blended.\nLADLE a thin layer of the FRESH ITALIAN SAUCE into the bottom of a deep-dish lasagne pan (or minimize recipe into a 13 x 9 baking dish; SPRINKLE 1 tablespoon of the freshly grated parmesan cheese over the sauce; ARRANGE a row of FRESH LASAGNE PASTA lengthwise over the cheese-sprinkled sauce (depending on pasta size, you may trim pasta with kitchen scissors to fit into baking dish if necessary); SPREAD 1/2 (HALF) of the FRESH SPINACH AND CHEESE FILLING over the pasta, leaving a 3/4 inch space around edges; SPRINKLE 1/3 of the mozzarella cheese over the filling; LADLE 1/3 of the SAUCE over the mozzarella, followed with 1 tablespoon freshly grated parmesan cheese.\nREPEAT layers in this order: (1) PASTA (2) the remaining FILLING (3) MOZZARELLA cheese (4) SAUCE (5) PARMESAN (6) remaining PASTA (7) remaining SAUCE (8) remaining MOZZARELLA; COVER with aluminum foil or casserole lid.\nBAKE covered in preheated 350 F degree oven for 30 minutes, then carefully slide out oven tray from oven using oven mitts; REMOVE the cover from dish carefully; then SPRINKLE the GARNISH (1 tablespoon freshly grated parmesan cheese, 2 teaspoons seasoned Italian breadcrumbs and 1 teaspoon finely minced fresh Italian parsley); LEAVE lasagne uncovered; CONTINUE to BAKE lasagne for 15 additional minutes; REMOVE from oven and allow to cool and set for 10 minutes; SLICE (using a serrated knife) and SERVE.\nSERVE and say, "MAMMA MIA!"!', 'instructions_list': ['PREP vegetables and herbs needed for the SAUTE FOR FRESH ITALIAN SAUCE (1 medium chopped onion, 8 ounces thinly sliced fresh mushrooms, 2/3 cup minced fresh basil leaves (reserving 1 tablespoon to refresh flavor later), 2-3 tablespoons minced fresh garlic, 3 tablespoons minced fresh Italian parsley, 2 tablespoons minced fresh oregano leaves, and 1 teaspoon minced fresh rosemary leaves); SAUTE in a large saucepan or pot in 1 tablespoon olive oil, between medium-low and medium heat until softened, about 7 minutes.', 'BRING 4 quarts unsalted water to boiling; CAREFULLY lower Roma tomatoes needed for recipe on a large spoon into boiling water; BLANCH until skins start to crack; REMOVE tomatoes and place into a colander; RINSE tomatoes under running cold water to remove skins; PUREE enough tomatoes to yield 3 1/4 cups; DICE remaining tomatoes to yield 3 1/4 cups; ADD both pureed and diced tomatoes to the saute mixture, along with 1/4 cup olive oil, 2-3 teaspoons ground fennel, 1/4 cup dry red wine, 2 teaspoons fine sea salt (if using fresh tomatoes), 1/4 teaspoon freshly grated lemon zest, 1/4 teaspoon freshly grated nutmeg, 1/4 teaspoon fresh ground black pepper and 1/4 teaspoon red pepper flakes; STIR in enough sugar or light corn syrup into SAUCE to balance acidity; RAISE HEAT to HIGH, stirring constantly until mixture begins to boil; REDUCE heat to MEDIUM-LOW, then SIMMER the sauce uncovered for 1 hour or slightly longer, stirring occasionally; REMOVE the SAUCE from heat; STIR in 1/4 cup freshly grated parmesan cheese and 1 tablespoon finely minced fresh basil leaves (to refresh flavor); SEASON to taste with fine sea salt if necessary.', 'IF PREPARING FRESH LASAGNE PASTA: While sauce is simmering: BEAT 3 eggs with 1 tablespoon olive oil gently in a medium bowl using a fork; into the large bowl of food processor MEASURE 1 cup semolina flour, 1/2 cup all-purpose flour and 3/8 teaspoon fine sea salt; PROCESS in food processor at least 30 seconds; with processor still running, very slowly POUR beaten eggs into feeder tube until all of the beaten eggs have been added; continue to PROCESS until dough becomes very thick and consistently blended (or when it forms a ball); REMOVE ball of dough from processor; WRAP dough tightly with plastic wrap; LET dough to rest at room temperature for 30 minutes. PLACE dough on a smooth clean surface dusted with semolina flour; ROLL out dough to 1/4 inch thick, SPRINKLE with semolina flour and repeat process until dough has a smooth, soft texture and with a balanced moisture level (not overly moist or dry); ROLL dough using a pasta machine (recommended), or a rolling pin to a 1/8 inch thickness, dusting very lightly with semolina flour if necessary, to prevent sticking; cut noodle dough into 2-3 inch width strips, with a 12" length; pasta does not need to be boiled first.', 'IF USING PACKAGED LASAGNE PASTA: MEASURE exactly 4 quarts of water (16 cups) into a large pot of water; BRING water to a full rolling boil; ADD 4 teasppoons kosher salt, then quickly but carefully add 9-12 pasta strips; COOK pasta until just tender (al dente), about 7 to 8 minutes; DRAIN lasagne noodles immediately in a large colander; REMOVE pasta individually using tongs and HANG pasta in (and over), the edges of the large pot and the colander to STRAIGHTEN, so that none of the noodles are touching; ALLOW to cool slightly.', 'PREPARE the PASTA BASTE by mixing 2 tablespoons olive oil with 1-2 cloves freshly pressed garlic (using a garlic press or mincing finely); BASTE lasagne noodles evenly on both sides in a 13 x 9 baking dish; REMOVE noodles and place aside.', 'WHIP the following ingredients of the FRESH SPINACH AND CHEESE FILLING in a large bowl, using an electric mixer: 3 cups whole milk ricotta cheese (Precious brand), 1 large egg, 2/3 cup freshly grated parmesan cheese, 1/4 cup cream, 1/4 teaspoon freshly grated lemon zest, 1/4 teaspoon freshly grated nutmeg, 1/4 teaspoon fine sea salt, 1/4 teaspoon freshly ground white pepper, and 1 small clove fresh mashed garlic (use a garlic press); FOLD in 1 cup finely chopped fresh spinach leaves and 2 tablespoons minced fresh basil leaves (stems removed), until mixture is thoroughly blended.', 'LADLE a thin layer of the FRESH ITALIAN SAUCE into the bottom of a deep-dish lasagne pan (or minimize recipe into a 13 x 9 baking dish; SPRINKLE 1 tablespoon of the freshly grated parmesan cheese over the sauce; ARRANGE a row of FRESH LASAGNE PASTA lengthwise over the cheese-sprinkled sauce (depending on pasta size, you may trim pasta with kitchen scissors to fit into baking dish if necessary); SPREAD 1/2 (HALF) of the FRESH SPINACH AND CHEESE FILLING over the pasta, leaving a 3/4 inch space around edges; SPRINKLE 1/3 of the mozzarella cheese over the filling; LADLE 1/3 of the SAUCE over the mozzarella, followed with 1 tablespoon freshly grated parmesan cheese.', 'REPEAT layers in this order: (1) PASTA (2) the remaining FILLING (3) MOZZARELLA cheese (4) SAUCE (5) PARMESAN (6) remaining PASTA (7) remaining SAUCE (8) remaining MOZZARELLA; COVER with aluminum foil or casserole lid.', 'BAKE covered in preheated 350 F degree oven for 30 minutes, then carefully slide out oven tray from oven using oven mitts; REMOVE the cover from dish carefully; then SPRINKLE the GARNISH (1 tablespoon freshly grated parmesan cheese, 2 teaspoons seasoned Italian breadcrumbs and 1 teaspoon finely minced fresh Italian parsley); LEAVE lasagne uncovered; CONTINUE to BAKE lasagne for 15 additional minutes; REMOVE from oven and allow to cool and set for 10 minutes; SLICE (using a serrated knife) and SERVE.', 'SERVE and say, "MAMMA MIA!"!'], 'language': 'en', 'nutrients': {'calories': '651', 'fatContent': '42.8', 'saturatedFatContent': '19.6', 'cholesterolContent': '183.6', 'sodiumContent': '1318', 'carbohydrateContent': '32.3', 'fiberContent': '3.5', 'sugarContent': '5.6', 'proteinContent': '34.3'}, 'site_name': None, 
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              'title': 'Mamma Mia! Fresh Italian Lasagne!', 'total_time': 135, 'yields': '12 servings'}]
# scraped_list[0]
# scraped_list[0].keys()

# def extract_ingredients_from_s3_event2(message):
#     # example_json = {
#     #     'uid': 'spanishsquash_906928', 
#     #     'url': 'https://www.allrecipes.com/recipe/73794/spanish-squash/',
#     #     'ingredients': ['1 pound ground beef', '1 tablespoon vegetable oil', '3 medium yellow squash, sliced', '1 small yellow onion, sliced', '1 (14.5 ounce) can diced tomatoes, drained', '0.5 cup water', '1 teaspoon chili powder', '0.25 teaspoon cumin', '1 dash garlic powder', 'salt and pepper to taste'] 
#     #     }
#     # batch_events = [example_json for i in range(4)]
#     # batch_events = [event for i in range(4)]
#     # batch_ingredients = [example_json["ingredients"] for i in range(5)]

#     # print(f"model: {model}")
#     print(f"=====================")
#     print(f'---->\n Value of message: {message}')
#     print(f"=====================")

#     # # s3_event = message["body"]
#     # s3_event = json.loads(message)["body"]

#     # print(f"=====================")
#     # print(f'---->\n Value of s3_event: {s3_event}')
#     # print(f"=====================")

#     # # # Extract the S3 bucket and the filename from the S3 event notification JSON object
#     # S3_BUCKET    = s3_event['Records'][0]['s3']['bucket']['name']
#     # S3_FILE_NAME = s3_event['Records'][0]['s3']['object']['key']

#     # print(f"- S3_BUCKET: {S3_BUCKET}")
#     # print(f"- S3_FILE_NAME: {S3_FILE_NAME}")

#     # print(f"Gathering JSON file from S3...")

#     # # get the object from S3
#     # s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_NAME)

#     # # read the JSON file into a dictionary
#     # s3_json = json.load(s3_obj["Body"])
    
#     s3_json = message
    
#     print(f"s3_json: {s3_json}")

#     # key of ingredients list in JSON object
#     ingredients_key = "ingredients"
#     # ingredients_key = "scraped_ingredients"

#     # extract food tags from ingredients list using FoodModel
#     food_tags = generate_tags(model, s3_json[ingredients_key])

#     print(f"--> food_tags: {food_tags}")
    
#     # Add FoodModel tags to JSON object
#     s3_json["ingredient_tags"] = food_tags
    
#     # # "scraped" in i.split("_")
#     # keep_keys = [i for i in s3_json.keys() if i == "uid" or  "scraped" in i.split("_")]
#     # keep_keys.insert(1, "url")

#     # final_json = {}

#     # for i in keep_keys:
#     #     print(f"i: {i}")
#     #     print(f"s3_json[i]: {s3_json[i]}")
#     #     if keep_keys == "url":
#     #         final_json[i] = s3_json["scraped_canonical_url"]
#     #     else:
#     #         # add the next key to the list of keys to keep
#     #         final_json[i] = s3_json[i]

#     # # remove the string "scraped_" from any keys in the final_json
#     # final_json = {key.replace("scraped_", ""): value for key, value in final_json.items()}

#     try:
#         s3_json = sanitize_json(s3_json)
#     except Exception as e:
#         print(f"Error sanitizing json: {e}")
#         return s3_json

#     return s3_json


# def clean_scraped_data2(df):

#     # # rename "title" column to "dish" 
#     # df = df.rename(columns={
#     #     "title": "dish", 
#     #     "canonical_url": "url",
#     #     "instructions_list": "directions", 
#     #     "ingredients": "quantities", 
#     #     "ingredient_tags": "ingredients",
#     #     "image" : "img", 
#     #     "site_name": "source",
#     #     "host": "base_url"
#     #     },
#     #     inplace=False)
    
#     # # Call clean_text function to clean and preprocess 'ingredients' column
#     # # convert the stringified list into a list for the ingredients, NER, and directions columns
#     # df['ingredients'] = df['ingredients'].apply(ast.literal_eval)
#     # df['quantities'] = df['quantities'].apply(ast.literal_eval)
#     # df['directions'] = df['directions'].apply(ast.literal_eval)

#     # remove any non alpha numerics and strip away any trailing/leading whitespaces
#     df['ingredients'] = df['ingredients'].apply(lambda x: [re.sub('[^A-Za-z ]', '', s).strip() for s in x])

#     # split up the words in the list of ingredients
#     # # # Call split_text function to split cleaned 'ingredients' column, creating a new 'split_ingredients' column
#     # df['split_ingredients'] = df['ingredients'].apply(lambda x: " ".join(x).split())

#     # df['split_ingredients'] = df['tmp_ingredients'].apply(split_text)

#     # # Reorder columns in the DataFrame
#     # df = df[['dish', 'ingredients', 'split_ingredients', "quantities", "directions"]]
#     # df = df[['dish', 'ingredients', 'split_ingredients', 'quantities', 'directions', 'link', 'id']]

#     # any dishes with missing values, replace with the word "missing"
#     df['dish'] = df['dish'].str.replace(r'[\x00-\x19]', '').replace('', 'missing')

#     # any category/cuisine with missing values, replace with the word "missing"
#     df['category'] = df['category'].str.replace(r'[\x00-\x19]', '').replace('', 'missing')
#     df['cuisine'] = df['cuisine'].str.replace(r'[\x00-\x19]', '').replace('', 'missing')
    
#     # split the category column into a list of strings
#     df['category'] = df['category'].str.split(',')
#     df['cuisine'] = df['cuisine'].str.split(',')

#     # santize list columns by removing unicode values
#     df['ingredients'] = df['ingredients'].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
#     # df['split_ingredients']  = df['split_ingredients'].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
#     df['quantities']  = df['quantities'].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
#     df['directions']  = df['directions'].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
#     df['category']    = df['category'].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
#     df['cuisine']     = df['cuisine'].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])

#     # coerce all time values to Int64 and replace missing/NaN values with 0
#     df['cook_time']  = pd.to_numeric(df['cook_time'], errors='coerce').astype('Int64').fillna(0)
#     df['prep_time']  = pd.to_numeric(df['prep_time'], errors='coerce').astype('Int64').fillna(0)
#     df['total_time'] = pd.to_numeric(df['total_time'], errors='coerce').astype('Int64').fillna(0)

#     # coerce all ratings values to float64 and replace missing/NaN values with 0
#     df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce').astype('float64').fillna(0)

#     # # List of column names that SHOULD contain list values
#     # list_columns = ['ingredients', 'quantities', 'directions']
#     # for column_name in list_columns:
#     #     is_list_column = df[column_name].apply(lambda x: isinstance(x, list)).all()
#     #     if not is_list_column:
#     #         # Coerce non-list values to lists
#     #         df[column_name] = df[column_name].apply(lambda x: [x] if not isinstance(x, list) else x)
#     #         # df[column_name] = df[column_name].apply(ast.literal_eval)

#     # add a row number column
#     df['n'] = np.arange(len(df))

#     # df['uid'] = df['dish'].apply(lambda x: "".join([re.sub('[^A-Za-z0-9]+', '', s).strip().lower() for s in x]))

#     df['uid']  = df['dish'].str.lower()
#     df['uid'] = df['uid'].str.replace('\W', '', regex=True)
#     df['uid'] = df['uid'] + "_" + df['n'].astype(str)
 
#     # sort by lowercased values
#     def lowercase_sort(lst):
#         return sorted(lst, key=lambda x: x.lower()) 
    
#     # sort the ingredients in each dish
#     df = df.assign(ingredients = lambda x: (x["ingredients"].apply(lowercase_sort)))

#     # df = df[['uid', 'dish', 'ingredients',
#     #            'split_ingredients',
#     #             'quantities', 'directions', 'description', 
#     #     'prep_time', 'cook_time', 'total_time', 
#     #     'yields', 
#     #     # 'nutrients', 
#     #     'category', 'cuisine','ratings',
#     #     'url', 'base_url', 'img', 'source']]
    
#     # convert a dictionary column to json  function:
#     def dict2json(dictionary):
#         return json.dumps(dictionary, ensure_ascii=False)
    
#     # convert list columns into dictonary columns
#     df["ingredients"] = df.apply(lambda row: {"ingredients":row['ingredients']}, axis=1)
#     # df["split_ingredients"] = df.apply(lambda row: {"split_ingredients":row['split_ingredients']}, axis=1)
#     df["quantities"] = df.apply(lambda row: {"quantities":row['quantities']}, axis=1)
#     df["directions"] = df.apply(lambda row: {"directions":row['directions']}, axis=1)
#     df["category"] = df.apply(lambda row: {"category":row['category']}, axis=1)
#     df["cuisine"] = df.apply(lambda row: {"category":row['cuisine']}, axis=1)

#     # convert dictionary columns to json columns
#     df["ingredients"] = df.ingredients.map(dict2json)
#     # df["split_ingredients"] = df.split_ingredients.map(dict2json)
#     df["quantities"] = df.quantities.map(dict2json)
#     df["directions"] = df.directions.map(dict2json)
#     df["category"] = df.category.map(dict2json)
#     df["cuisine"] = df.cuisine.map(dict2json)

#     # Add a unique dish_id to act as the primary key
#     df["dish_id"] = df.index
    
#     # # Reorder columns in the DataFrame
#     # df = df[['uid', 'dish', 'ingredients', 'split_ingredients', "quantities", "directions", "url", "base_url", "img"]]

#     # Reorder and select columns in the DataFrame
#     df = df[['dish_id', 'uid', 'dish', 'ingredients', 
#             #  'split_ingredients', 
#              'quantities', 'directions', 'description',
#             'prep_time', 'cook_time', 'total_time', 'yields',  # 'nutrients', 
#             'category', 'cuisine','ratings', 'url', 'base_url', 'img', 'source']]
    
#     return df