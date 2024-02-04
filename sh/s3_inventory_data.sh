# ----------------------------------------------------------------------------------
# ----- Generate a testing S3 inventory manifest.json and CSV example datasets -----
# ----------------------------------------------------------------------------------
# REAL S3 URI to put into CSV_CONTENT:
# s3://recipes-output-bucket/2024/01/22/0550fd8d521a4af798c82a150a2c3543_1705930721.csv
# s3://recipes-output-bucket/2024/01/22/61ff10e04ff549719f7294cb29dbcbd8_1705930724.csv
# s3://recipes-output-bucket/2024/01/22/c1412ca2aeb24a6ea0038b769c1587b0_1705930726.csv

# Paths to save local CSV and JSON files to defaults to current directory if arguments are NOT provided
LOCAL_JSON_PATH=${1:-"./manifest.json"}
LOCAL_CSV_PATH=${2:-"./s3_inventory_example.csv"}

LOCAL_CSV_GZ_PATH=${3:-"./s3_inventory_example.gz.csv"}

echo "Local JSON path: $LOCAL_JSON_PATH"
echo "Local CSV path: $LOCAL_CSV_PATH"
echo "Local GZ CSV path: $LOCAL_CSV_GZ_PATH"

# # CSV headers for s3_inventory_example.csv
# CSV_CONTENT="Bucket,Key,VersionId,IsLatest,LastModified,ETag,Size,StorageClass,Owner,Tags
# example-bucket,example-folder/example-file.txt,,true,2024-02-03T10:15:30Z,"e4d909c290d0fb1ca068ffaddf22cbd0",1024,STANDARD,123456789012,"key1=value1,key2=value2"
# example-bucket,another-folder/another-file.txt,,true,2024-02-02T08:20:15Z,"3c01bdbb26f358bab27f267924aa2c9a",2048,STANDARD,123456789012,"key3=value3"
# "

CSV_CONTENT="Bucket,Key,VersionId,IsLatest,LastModified,ETag,Size,StorageClass,Owner,Tags
recipes-output-bucket,2024/01/22/0550fd8d521a4af798c82a150a2c3543_1705930721.csv,,,,,,,
recipes-output-bucket,2024/01/22/61ff10e04ff549719f7294cb29dbcbd8_1705930724.csv,,,,,,,
recipes-output-bucket,2024/01/22/c1412ca2aeb24a6ea0038b769c1587b0_1705930726.csv,,,,,,,"

# Check if the local CSV file already exists
if [ ! -f "$LOCAL_CSV_PATH" ]; then
    # Create an empty CSV file with headers
    echo "$CSV_CONTENT" > "$LOCAL_CSV_PATH"
    echo "Empty CSV file created: $LOCAL_CSV_PATH"
else
    echo "CSV file $LOCAL_CSV_PATH already exists."
fi

# Compress the CSV file to .csv.gz format
gzip -c "$LOCAL_CSV_PATH" > "$LOCAL_CSV_GZ_PATH"

echo "Compressed CSV (gz) file created: $LOCAL_CSV_GZ_PATH"

# Define manifest data in JSON format
MANIFEST_JSON='{
    "sourceBucket": "recipes-output-bucket",
    "destinationBucket": "arn:aws:s3:::recipes-output-bucket-inventory",
    "version": "2016-11-30",
    "creationTimestamp": "12:10:00",
    "fileFormat": "CSV",
    "fileSchema": "Bucket, Key, VersionId, IsLatest, IsDeleteMarker, Size, LastModifiedDate, ETag, StorageClass, IsMultipartUploaded, ReplicationStatus, EncryptionStatus, ObjectLockRetainUntilDate, ObjectLockMode, ObjectLockLegalHoldStatus, IntelligentTieringAccessTier, BucketKeyStatus, ChecksumAlgorithm, ObjectAccessControlList, ObjectOwner",
    "files": [
        {
            "key": "s3_inventory_example.gz.csv",
            "size": 2147483647
        }
    ]
}'

# Write the JSON data to the manifest file
echo "$MANIFEST_JSON" > "$LOCAL_JSON_PATH"

echo "Manifest JSON file created: $LOCAL_JSON_PATH"

# # ----------------------------------------------------------------------------------
# # ----- Generate a testing S3 inventory manifest.json and CSV example datasets -----
# # ----------------------------------------------------------------------------------
# # REAL S3 URI to put into CSV_CONTENT:
# # s3://recipes-output-bucket/2024/01/22/0550fd8d521a4af798c82a150a2c3543_1705930721.csv
# # s3://recipes-output-bucket/2024/01/22/61ff10e04ff549719f7294cb29dbcbd8_1705930724.csv
# # s3://recipes-output-bucket/2024/01/22/c1412ca2aeb24a6ea0038b769c1587b0_1705930726.csv

# # Paths to save local CSV and JSON files to defaults to current directory if arguments are NOT provided
# LOCAL_JSON_PATH=${1:-"./manifest.json"}

# LOCAL_JSON_PATH1=${1:-"./manifest.json"}

# LOCAL_JSON_PATH2="./recipes-output-bucket-inventory/recipes-output-bucket/daily-inventory/2024-02-02T00-00Z/s3_inventory_example3.gz.csv"
# LOCAL_CSV_PATH1=${2:-"./s3_inventory_example1.csv"}
# # LOCAL_CSV_GZ_PATH1=${3:-"./s3_inventory_example1.gz.csv"}
# LOCAL_CSV_GZ_PATH1=${3:-"./recipes-output-bucket-inventory/recipes-output-bucket/daily-inventory/data/s3_inventory_example3.gz.csv"}

# OCAL_CSV_PATH2=${4:-"./s3_inventory_example2.csv"}
# LOCAL_CSV_GZ_PATH2=${5:-"./recipes-output-bucket-inventory/recipes-output-bucket/daily-inventory/data/s3_inventory_example2.gz.csv"}

# # LOCAL_CSV_GZ_PATH=${3:-"./s3_inventory_example.gz.csv"}

# echo "Local JSON path: $LOCAL_JSON_PATH"
# echo "Local CSV path: $LOCAL_CSV_PATH"
# echo "Local GZ CSV path: $LOCAL_CSV_GZ_PATH"

# # # CSV headers for s3_inventory_example.csv
# # CSV_CONTENT="Bucket,Key,VersionId,IsLatest,LastModified,ETag,Size,StorageClass,Owner,Tags
# # example-bucket,example-folder/example-file.txt,,true,2024-02-03T10:15:30Z,"e4d909c290d0fb1ca068ffaddf22cbd0",1024,STANDARD,123456789012,"key1=value1,key2=value2"
# # example-bucket,another-folder/another-file.txt,,true,2024-02-02T08:20:15Z,"3c01bdbb26f358bab27f267924aa2c9a",2048,STANDARD,123456789012,"key3=value3"
# # "

# CSV_CONTENT="Bucket,Key,VersionId,IsLatest,LastModified,ETag,Size,StorageClass,Owner,Tags
# recipes-output-bucket,2024/01/22/0550fd8d521a4af798c82a150a2c3543_1705930721.csv,,,,,,,
# recipes-output-bucket,2024/01/22/61ff10e04ff549719f7294cb29dbcbd8_1705930724.csv,,,,,,,
# recipes-output-bucket,2024/01/22/c1412ca2aeb24a6ea0038b769c1587b0_1705930726.csv,,,,,,,"


# # Check if the local CSV file already exists
# if [ ! -f "$LOCAL_CSV_PATH" ]; then
#     # Create an empty CSV file with headers
#     echo "$CSV_CONTENT" > "$LOCAL_CSV_PATH"
#     echo "Empty CSV file created: $LOCAL_CSV_PATH"
# else
#     echo "CSV file $LOCAL_CSV_PATH already exists."
# fi

# # Compress the CSV file to .csv.gz format
# gzip -c "$LOCAL_CSV_PATH" > "$LOCAL_CSV_GZ_PATH"

# echo "Compressed CSV (gz) file created: $LOCAL_CSV_GZ_PATH"

# # Define manifest data in JSON format
# MANIFEST_JSON='{
#     "sourceBucket": "recipes-output-bucket",
#     "destinationBucket": "arn:aws:s3:::recipes-output-bucket-inventory",
#     "version": "2016-11-30",
#     "creationTimestamp": "'$(date +%s)'000",
#     "fileFormat": "CSV",
#     "fileSchema": "Bucket, Key, VersionId, IsLatest, IsDeleteMarker, Size, LastModifiedDate, ETag, StorageClass, IsMultipartUploaded, ReplicationStatus, EncryptionStatus, ObjectLockRetainUntilDate, ObjectLockMode, ObjectLockLegalHoldStatus, IntelligentTieringAccessTier, BucketKeyStatus, ChecksumAlgorithm, ObjectAccessControlList, ObjectOwner",
#     "files": [
#         {
#             "key": "recipes-output-bucket/daily-inventory/2024-02-02T00-00Z/data/s3_inventory_example.csv.gz",
#             "size": 2147483647,
#             "MD5checksum": "'$(openssl rand -hex 16 | tr -d "\n")'"
#         }
#     ]
# }'

# # Write the JSON data to the manifest file
# echo "$MANIFEST_JSON" > "$LOCAL_JSON_PATH"

# echo "Manifest JSON file created: $LOCAL_JSON_PATH"