
S3_BUCKET="recipes-output-bucket"
PATH_TO_S3_MANIFEST="/Users/anguswatters/Desktop/s3_object_manifest.csv"


import datetime
import subprocess

import boto3
import pandas as pd


s3_manifest = pd.read_csv(PATH_TO_S3_MANIFEST)

# check if the object is in the manifest and if its copy_complete is True
# if its not in the manifest or its in the manifest but the copy_complete is False, then add the file name to a list
# then copy the files in the list to the new bucket
# then update the manifest with the new files and set the copy_complete to True
# then delete the file from local storage
# if the file is in the manifest and the copy_complete is True, then delete the file from local storage

def process_and_update_manifest(manifest_df, recent_obj_df, s3_bucket):
    # Logic to process files and update manifest
    new_rows = []

    for index, row in recent_obj_df.iterrows():
        file_name = row['s3_object_key']

        # Check if the file is already in the manifest
        if file_name not in manifest_df['s3_object_key'].tolist():
            # Copy file to new bucket and update manifest
            print(f"Copying file {file_name} to new bucket...")
            # Add logic to copy the file to the new bucket
            # ...

            # Update manifest
            new_rows.append({
                'last_modified': row['last_modified'],
                'size': row['size'],
                's3_bucket': s3_bucket,
                's3_object_key': file_name,
                'copy_complete': False
            })

            print(f"File {file_name} copied and manifest updated.")

            # Delete local file
            print(f"Deleting local file {file_name}...")
            # Add logic to delete the local file
            # ...

    if new_rows:
        print(f"Adding {len(new_rows)} new rows to the manifest...")
        # Concatenate new rows to the existing manifest_df
        manifest_df = pd.concat([manifest_df, pd.DataFrame(new_rows)], ignore_index=True)

    return manifest_df

def parse_s3_ls_output(output_text, s3_bucket):
    # Return an empty DataFrame if output_text is empty
    if not output_text:
        return pd.DataFrame(columns=['last_modified', 'size', 's3_bucket','s3_object_key', 'copy_complete'])


    # Initialize lists to store parsed data
    last_modified_list = []
    size_list = []
    file_name_list = []

    # Parse the output text
    for line in output_text.split('\n'):
        if line:
            # Split each line into columns (assuming the default format of `aws s3 ls`)
            columns = line.split()

            # Extract relevant information (adjust indices based on the actual format)
            last_modified = f"{columns[0]} {columns[1]}"
            size = columns[2]
            file_name = ' '.join(columns[3:])

            # Append data to lists
            last_modified_list.append(last_modified)
            size_list.append(size)
            file_name_list.append(file_name)

    # Create a pandas DataFrame
    df = pd.DataFrame({
        'last_modified': last_modified_list,
        'size': size_list,
        's3_bucket': s3_bucket,
        's3_object_key': file_name_list,
        'copy_complete': False
    })

    return df

# 
date = datetime.datetime.now().strftime("%Y-%m-%d")

# Run the command
list_s3_obj_cmd = f"aws s3 ls s3://{S3_BUCKET} --recursive | grep \"{date}\""
s3_list = subprocess.run(list_s3_obj_cmd, shell=True, text=True, stdout=subprocess.PIPE)

output_text = s3_list.stdout

# Parse the output
daily_objects = parse_s3_ls_output(output_text, S3_BUCKET)

updated_manifest = process_and_update_manifest(s3_manifest, daily_objects, S3_BUCKET)
updated_manifest.s3_object_key.tolist()

# Steps to take to process new files
# Take filename and append with S3 bucket
# copy the S3 object to local file
# IMPORT/COPY the CSV file into the database (or I could read the CSV into Pandas and run df.to_sql()) - Confirm the COPY command works
# if the IMPORT/COPY command works, delete the local file and update the file manifest "copy_complete" column to True

# filter updated_manifest for files where copy_complete is False
# copy the file to local storage
# import the file to the database
# update the manifest with copy_complete = True
# delete the local file
files_to_process = updated_manifest.loc[updated_manifest['copy_complete'] == False]

for index, row in files_to_process.iterrows():
    print(f"index: {index}")
    print(f"Processing file {row['s3_object_key']}...")
    # Take filename and append with S3 bucket
    s3_object_path = f"s3://{row['s3_bucket']}/{row['s3_object_key']}"

    # save_path = f"/usr/local/s3_downloads/{s3_object_path}"
    save_path = f"/Users/anguswatters/Desktop/{s3_object_path}"

    # copy the S3 object to local file in s3_downloads/
    copy_s3_obj_cmd = f"aws s3 cp {s3_object_path} {save_path}"

    s3_copy = subprocess.run(copy_s3_obj_cmd, shell=True, text=True, stdout=subprocess.PIPE)

    # read 
    # use the following bash command to import the file into the database, but run it from python script: 
    # # copy dish recipes CSV into recipe_table
    # sudo -u postgres psql -d ${DB_NAME} -c "\copy recipe_table FROM 'usr/local/s3_downloads/${S3_FILE}' DELIMITER ',' CSV HEADER;"
    # # copy ingredient recipes CSV into recipe_table
    # sudo -u postgres psql -d ${DB_NAME} -c "\copy recipe_table FROM 'usr/local/s3_downloads/${S3_FILE}' DELIMITER ',' CSV HEADER;"
    
    # copy command to copy local CSV into database recipe_table
    try:
        subprocess.run(f"sudo -u postgres psql -d {DB_NAME} -c \"\copy recipe_table FROM '{save_path}' DELIMITER ',' CSV HEADER;\"", shell=True, text=True, stdout=subprocess.PIPE)
        print(f"Successfully imported file {row['s3_object_key']} into database.")
    except:
        print(f"Error importing file {row['s3_object_key']} into database.")

    # update the manifest with copy_complete = True
    updated_manifest.loc[index, 'copy_complete'] = True

    # delete the local file
    subprocess.run(f"rm {save_path}", shell=True, text=True, stdout=subprocess.PIPE)

    # overwrite the manifest with the updated manifest
    updated_manifest.to_csv(PATH_TO_S3_MANIFEST, index=False)    

    # if the IMPORT/COPY command works, delete the local file and update the file manifest "copy_complete" column to True


# Check if the object is in the manifest and if its copy_complete is True
# If it's not in the manifest or it's in the manifest but the copy_complete is False,
# then add the file name to a list
new_files = []
for file_name in daily_objects["file_name"].tolist():
    if file_name not in s3_manifest['file_name'].tolist() or not s3_manifest.loc[s3_manifest['file_name'] == file_name, 'copy_complete'].bool():
        new_files.append(file_name)

# Process and update manifest for new files
if new_files:
    s3_manifest = process_and_update_manifest(s3_manifest, new_files)

# Save the updated manifest
s3_manifest.to_csv(PATH_TO_S3_MANIFEST, index=False)