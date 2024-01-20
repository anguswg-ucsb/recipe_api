###############################################################################
#### S3 notification for initial raw CSV upload to trigger lambda function ####
###############################################################################

# S3 event notification for raw data bucket to trigger lambda function
resource "aws_s3_bucket_notification" "raw_s3_bucket_notification" {
  bucket = aws_s3_bucket.raw_s3_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.chunk_csv_lambda_function.arn
    events              = ["s3:ObjectCreated:*"]
    # filter_prefix       = "raw/"
    filter_suffix       = ".csv"
  }
}

# # Create S3 event notification to send messages to SQS queue when a JSON file is uploaded to the raw S3 bucket
# resource "aws_s3_bucket_notification" "raw_s3_bucket_notification" {
#   bucket = aws_s3_bucket.raw_s3_bucket.id

#   queue {
#     queue_arn     = aws_sqs_queue.sqs_to_scrape_queue.arn
#     events        = ["s3:ObjectCreated:*"]
#     filter_suffix = ".json"
#   }
# }

# # Create S3 event notification to send messages to SQS queue when a JSON file is uploaded to the raw S3 bucket
# resource "aws_s3_bucket_notification" "raw_s3_bucket_notification" {
#   bucket = aws_s3_bucket.raw_s3_bucket.id

#   queue {
#     queue_arn     = aws_sqs_queue.sqs_to_scrape_queue.arn
#     events        = ["s3:ObjectCreated:*"]
#     filter_suffix = ".csv"
#   }
# }

############################################################################################################
#### S3 notification to send SQS now that new scraped data is ready to be processed by lambda consumer #####
############################################################################################################

# Create S3 event notification to send messages to SQS queue 
# when a JSON file is uploaded to the STAGE S3 bucket (scraped data)
resource "aws_s3_bucket_notification" "stage_s3_bucket_notification" {
  bucket = aws_s3_bucket.stage_s3_bucket.id

  queue {
    queue_arn     = aws_sqs_queue.sqs_process_staged_queue.arn
    events        = ["s3:ObjectCreated:*"]
    # filter_suffix = ".json"
    filter_suffix = ".csv"
  }
}

############################################################################################################
#### S3 notification to send SQS OUTPUT CSVs for EC2 to consume #####
############################################################################################################

# Create S3 event notification to send messages to SQS queue 
# when a final OUTPUT.csv file is uploaded to the OUTPUT S3 bucket 
resource "aws_s3_bucket_notification" "output_s3_bucket_notification" {
  bucket = data.aws_s3_bucket.output_s3_bucket.id

  queue {
    queue_arn     = aws_sqs_queue.sqs_output_queue.arn
    events        = ["s3:ObjectCreated:*"]
    # filter_suffix = ".json"
    filter_suffix = ".csv"
  }
}