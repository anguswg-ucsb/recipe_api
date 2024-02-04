#!/usr/bin/env python3

# Script for restoring POSTGRES database data from S3 inventory which describes the location of the CSV files in the output bucket

# General utility libraries
import os
import subprocess

import gzip
import json
import csv

import time
import datetime
from datetime import timedelta, datetime

# AWS SDK for Python
import boto3

# Pandas for data manipulation
import pandas as pd

# Environment variables
DB_NAME           = os.environ.get("DB_NAME")

DB_USERNAME       = os.environ.get("DB_USERNAME")
DB_PASSWORD       = os.environ.get("DB_PASSWORD")

AWS_REGION        = os.environ.get("AWS_REGION")

S3_SOURCE_BUCKET  = os.environ.get("S3_SOURCE_BUCKET")
S3_INVENTORY_BUCKET = os.environ.get("S3_INVENTORY_BUCKET")
INVENTORY_CONFIG_ID = os.environ.get("INVENTORY_CONFIG_ID")
S3_DOWNLOADS_PATH = os.environ.get("S3_DOWNLOADS_PATH")

S3_SOURCE_BUCKET = "recipes-output-bucket"
S3_INVENTORY_BUCKET = "recipes-output-bucket-inventory"
INVENTORY_CONFIG_ID = "RecipesOutputDailyInventory"

S3_INVENTORY_URI = "s3://" + S3_INVENTORY_BUCKET
S3_DAILY_INVENTORY_PATH = "s3://" + S3_INVENTORY_BUCKET + "/" + "daily-inventory" + "/" + S3_SOURCE_BUCKET + "/" + INVENTORY_CONFIG_ID + "/"

S3_INVENTORY_PREFIX = "daily-inventory"

MANIFEST_JSON_PATH = './manifest.json'

print(f"---->\n Value of S3_SOURCE_BUCKET: {S3_SOURCE_BUCKET}")
print(f"---->\n Value of S3_INVENTORY_BUCKET: {S3_INVENTORY_BUCKET}")
print(f"---->\n Value of S3_INVENTORY_URI: {S3_INVENTORY_URI}")
print(f"---->\n Value of S3_DAILY_INVENTORY_PATH: {S3_DAILY_INVENTORY_PATH}")
print(f"---->\n Value of S3_DOWNLOADS_PATH: {S3_DOWNLOADS_PATH}")
print(f"---->\n Value of MANIFEST_JSON_PATH: {MANIFEST_JSON_PATH}")

# Construct a list of dates 'n' days before the provided date 'timestamp' (in the format "YYYY-MM-DDTHH:MM:SSZ")
def get_dates_before_now(n = 1, precision = "day"):

    # output list of dates
    date_list = []

    # Iterate over n days
    for i in range(1, n + 1):

        timestamp = datetime.now()

        # Get date i days before the current date
        date_before = timestamp - timedelta(days=i)

        if precision == "minute":
            # Format the date as YYYY-MM-DDTHH:MM:SSZ
            formatted_date = date_before.strftime("%Y-%m-%dT%H:%MZ")
        elif precision == "hour":
            # Format the date as YYYY-MM-DDTHH:00Z
            formatted_date = date_before.strftime("%Y-%m-%dT00:00Z")
        elif precision == "day":
            # round the date to the nearest day
            formatted_date = date_before.strftime("%Y-%m-%d")
        else:
            # round the date to the nearest day
            formatted_date = date_before.strftime("%Y-%m-%d")

        # Append the formatted date to the list
        date_list.append(formatted_date)

    return date_list

# current_date = datetime.datetime.now()

get_dates_before_now(7)

def get_manifest_keys(inventory_bucket, source_bucket, prefix, config_id):
    
        # # Create the S3 client
        # s3 = boto3.client("s3", region_name=AWS_REGION)
        date_list = get_dates_before_now(3)

        # Create the list of manifest keys
        manifest_keys = []
    
        # Iterate over the list of dates
        for date in date_list:
            # Construct the manifest key
            # manifest_key = f"{s3_inventory_uri}/daily-inventory/{inventory_config_id}/{date}/manifest.json"
            manifest_key = f"s3://{inventory_bucket}/{prefix}/{source_bucket}/{config_id}/{date}/manifest.json"
            # manifest_key = "s3://" + inventory_bucket + "/" + prefix + "/" + source_bucket + "/" + config_id + "/" {date}/manifest.json

            # Append the manifest key to the list
            manifest_keys.append(manifest_key)
    
        return manifest_keys

manifest_keys = get_manifest_keys(S3_INVENTORY_BUCKET, S3_SOURCE_BUCKET, S3_INVENTORY_PREFIX, INVENTORY_CONFIG_ID)
manifest_keys[0]

def list_bucket_inventory_contents(sess, *, bucket, manifest_key):
    """
    Iterate through the contents of an S3 Bucket Inventory.

    This only supports an Inventory created in CSV format; it doesn't
    support Apache Parquet or Apache ORC.
    """
    s3 = sess.client("s3")

    # Download and parse the inventory manifest.
    #
    # This tells us where the individual inventory files are located,
    # and the schema of those files.
    #
    # See https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-inventory-location.html#storage-inventory-location-manifest
    manifest_obj = s3.get_object(Bucket=bucket, Key=manifest_key)
    manifest = json.load(manifest_obj["Body"])

    if manifest["fileFormat"] != "CSV":
        raise ValueError("This function only supports an S3 Inventory in CSV format")

    schema = [s.strip() for s in manifest["fileSchema"].split(",")]

    # Go through each of the files in the manifest, and download them
    # from S3.  Then unpack them and parse them as CSV.
    for f in manifest["files"]:
        s3_obj = s3.get_object(Bucket=bucket, Key=f["key"])

        with gzip.open(s3_obj["Body"], "rt") as infile:
            reader = csv.reader(infile)

            for row in reader:

                # Combine the data in the row with the field names we
                # got from the schema in the manifest.
                data = dict(zip(schema, row))

                # Because the data comes from a CSV, it's all strings.
                # Turn it into some slightly nicer types.
                data["Size"] = int(data["Size"])
                data["IsLatest"] = data["IsLatest"] == "true"
                data["IsDeleteMarker"] = data["IsDeleteMarker"] == "true"
                data["LastModifiedDate"] = datetime.datetime.strptime(
                    data["LastModifiedDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )

                # If an object doesn't have a VersionId, we still get
                # an empty string in the CSV -- delete the key to mimic
                # the behaviour of the ListObjectsV2 API.
                if data["VersionId"] == "":
                    del data["VersionId"]

                yield data
# ######
# tmp = pd.read_csv('/Users/anguswatters/Downloads/9d01169a86e24fb8867823a6fcd249a6_1705762724.csv')
# tmp = pd.read_csv('/Users/anguswatters/Downloads/5dbe3e1610654706bd4da237da7be2bd_1705762730.csv')

# tmp
# len(create_unique_ingredients(tmp))
MANIFEST_JSON_PATH = './manifest.json'

# Read the JSON file
with open(MANIFEST_JSON_PATH, 'r') as json_file:
    manifest = json.load(json_file)

manifest.keys()

def list_keys(manifest):
    gzip_list = []
    for obj in manifest['files']:

        print(f"obj: {obj}")
        print(f"obj['key']: {obj['key']}")

        gzip_list.append(obj['key'])

        # gzip_obj = s3.Object(bucket_name=bucket, key=obj['key'])
        # buffer = gzip.open(gzip_obj.get()["Body"], mode='rt')
        # reader = csv.reader(buffer)
        # for row in reader:
        #     yield row
    return gzip_list

manifest_keys = list_keys(manifest)

manifest_keys
manifest_keys

inventory = pd.read_csv(f"/Users/anguswatters/Desktop/github/recipe_api/{manifest_keys[0]}", compression='gzip')

inventory


# ######
# --------------------------------
# ---- Recipes data functions ----
# functions for upserting new CSV data into database from an SQS queue
# --------------------------------


# SQS consumer main function
# - Long poll for message on SQS queue
# - When new messages come in, loop through the batch of messages
# - For each message call 'upsert_s3_data_into_db()' to: 
    # --> DOWNLOAD the object from S3
    # --> UPSERT it into the database
    # --> CREATE unique ingredients
    # --> UPSERT unique ingredients
    # --> DELETE the local file
def main() -> None:

    s3 = boto3.client("s3", region_name=AWS_REGION)
    sqs = boto3.client("sqs", region_name=AWS_REGION)

    empty_response_count = 0  # Initialize the count of consecutive empty responses

    while True:
        print(f"----------------------------------------")
        print(f"---- STARTING NEW POLLING ITERATION ----")
        print(f"empty_response_count: {empty_response_count}")
        print(f"----------------------------------------")
        
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
    
            # Get the S3 bucket and object key from the message
            s3_bucket       = msg_body["Records"][0]["s3"]["bucket"]["name"]
            s3_object_key   = msg_body["Records"][0]["s3"]["object"]["key"]

            # Get the filename from the object key
            s3_key_filename = os.path.basename(s3_object_key)

            # Create the local file path to save the S3 object to
            local_file_path = f"{S3_DOWNLOADS_PATH}/{s3_key_filename}"

            print(f"----" * 6)
            print(f"- s3_bucket: {s3_bucket}")
            print(f"- s3_object_key: {s3_object_key}")
            print(f"- s3_key_filename: {s3_key_filename}")
            print(f"- local_file_path: {local_file_path}")
            print(f"----" * 6)
            print(f"Attempting download and insert of S3 CSV...")

            # Download the object from S3, copy it into the database, and delete the local file
            # insert_s3_obj_into_db(s3, s3_bucket, s3_object_key, local_file_path)
            upsert_s3_data_into_db(s3, s3_bucket, s3_object_key, local_file_path)

            print(f"Successfully downloaded and inserted new S3 CSV!")

            # recipes_df = pd.read_csv(local_file_path)

            # # Create unique ingredients dataset
            # unique_ingreds = create_unique_ingredients(recipes_df, json_column = "ingredient_tags")

            # TODO: If successful, delete the message from the SQS queue
            # sqs.delete_message(
            #     QueueUrl=SQS_QUEUE_URL,
            #     ReceiptHandle=msg["ReceiptHandle"]
            # )
            

            print(f"====" * 7)
            print(f"====" * 7)

# Run the SQS consumer main function
if __name__ == "__main__":
    main()