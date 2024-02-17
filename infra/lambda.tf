
#########################################################################################################
####################################################
########### Datapipline Lambda Functions ###########
####################################################
#########################################################################################################

###################################################################
#  Lambda function (Triggered by CSV ObjectCreated in S3 bucket) #
###################################################################

resource "aws_lambda_function" "chunk_csv_lambda_function" {
    s3_bucket        = aws_s3_bucket.lambda_s3_bucket.bucket
    s3_key           = var.chunk_csv_lambda_zip_file_name
    s3_object_version = aws_s3_object.chunk_csv_lambda_code_object.version_id
    source_code_hash = var.chunk_csv_lambda_zip_file_name

    function_name    = var.chunk_csv_lambda_function_name
    handler          = var.chunk_csv_lambda_handler
    # handler          = "chunk_csv.chunk_csv.chunk_csv"

    role             = aws_iam_role.recipe_pipeline_lambda_role.arn
    runtime          = "python3.11"
    architectures    = ["x86_64"]
    # architectures    = ["arm64"]

    # timeout in seconds
    timeout         = 900

    # Only allow a maximum of 5 Lambdas to be run concurrently
    reserved_concurrent_executions = 5

    # Attach the Lambda function to the CloudWatch Logs group
    environment {
        variables = {
            CW_LOG_GROUP         = aws_cloudwatch_log_group.chunk_csv_lambda_log_group.name,
            SQS_QUEUE_URL        = aws_sqs_queue.sqs_csv_chunk_queue.url
        }
    }
}

##################################################################################################################
# Lambda SQS Event Source Mapping (map CSV chunk lambda to S3 event notification for when a new CSV is uploaded) #
##################################################################################################################

# Allow S3 Event notifications to invoke the Chunk CSV Lambda function
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.chunk_csv_lambda_function.arn}"
  principal = "s3.amazonaws.com"
  source_arn = "${aws_s3_bucket.raw_s3_bucket.arn}"
}

########################################################
# Lambda function (Send JSON recipes to SQS to scrape) #
########################################################

# lambda function consumes chunked CSV SQS queue and iterates over chunk of CSV in S3 and sends each row as a JSON message to the SQS "to scrape" queue
resource "aws_lambda_function" "csv_to_json_lambda_function" {
  s3_bucket         = aws_s3_bucket.lambda_s3_bucket.bucket
  s3_key            = var.csv_to_json_lambda_zip_file_name
  s3_object_version = aws_s3_object.csv_to_json_lambda_code_object.version_id
  source_code_hash  = var.csv_to_json_lambda_zip_file_name
  # source_code_hash = filebase64sha256(local.csv_to_json_zip)

  function_name    = var.csv_to_json_lambda_function_name
  handler          = var.csv_to_json_lambda_handler
  # handler          = "csv_to_json.csv_to_json.csv_to_json"

  role             = aws_iam_role.recipe_pipeline_lambda_role.arn
  runtime          = "python3.11"
  architectures    = ["x86_64"]
  # architectures    = ["arm64"]

  # timeout in seconds
  timeout         = 900

  # Only allow for a maximum of 8 Lambdas to be run concurrently
  reserved_concurrent_executions = 5
  
  # Attach the Lambda function to the CloudWatch Logs group
  environment {
    variables = {
        CW_LOG_GROUP         = aws_cloudwatch_log_group.csv_to_json_lambda_log_group.name,
        CHUNK_SQS_QUEUE_URL     = aws_sqs_queue.sqs_csv_chunk_queue.url,
        OUTPUT_SQS_QUEUE_URL     = aws_sqs_queue.sqs_to_scrape_queue.url,
    }
  }

  depends_on = [
    aws_s3_bucket.lambda_s3_bucket,
    aws_s3_object.csv_to_json_lambda_code_object,
    # aws_s3_bucket_notification.raw_s3_bucket_notification,
    aws_iam_role_policy_attachment.lambda_logs_policy_attachment,
    aws_cloudwatch_log_group.csv_to_json_lambda_log_group
  ]
  
  tags = {
    name              = local.name_tag
    resource_category = "lambda"
  }
}

#####################################################################################################
# Lambda SQS Event Source Mapping (Allows Chunk CSV SQS Queue to trigger send JSON lambda function) #
#####################################################################################################

# Lambda SQS Event Source Mapping
resource "aws_lambda_event_source_mapping" "send_json_lambda_sqs_event_source_mapping" {
  event_source_arn = aws_sqs_queue.sqs_csv_chunk_queue.arn
  function_name    = aws_lambda_function.csv_to_json_lambda_function.function_name
  batch_size       = 1
  depends_on = [
    aws_lambda_function.csv_to_json_lambda_function,
    aws_sqs_queue.sqs_csv_chunk_queue,
  ]
}

# Allow the "CSV chunk" SQS queue to invoke the Send JSON Lambda function
resource "aws_lambda_permission" "allow_sqs_invoke_send_json_lambda" {
  statement_id  = "AllowSQSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.csv_to_json_lambda_function.arn}"
  principal = "sqs.amazonaws.com"
  source_arn = "${aws_sqs_queue.sqs_csv_chunk_queue.arn}"
}

####################################################################################
# Lambda function (Recipe Scraper - Triggered by new recipe messages in SQS queue) #
####################################################################################

# lambda function triggered when a JSON file is uploaded to the raw S3 bucket (ObjectCreated)
# Function loads the JSON data and gets more data from the URL in the JSON and
# adds to new found data to the original JSON, then uploads this to the staging bucket
resource "aws_lambda_function" "recipes_scraper_lambda_function" {
  s3_bucket        = aws_s3_bucket.lambda_s3_bucket.bucket
  s3_key           = var.recipes_scraper_lambda_zip_file_name
  s3_object_version = aws_s3_object.recipes_scraper_lambda_code_object.version_id
  source_code_hash = var.recipes_scraper_lambda_zip_file_name
  # source_code_hash = filebase64sha256(local.recipes_scraper_zip)
  # source_code_hash = aws_s3_object.recipes_scraper_lambda_code_object.etag

  function_name    = var.recipes_scraper_lambda_function_name
  handler          = var.recipes_scraper_lambda_handler

  # handler          = "recipes_scraper.recipes_scraper.recipes_scraper"
  role             = aws_iam_role.recipe_pipeline_lambda_role.arn
  runtime          = "python3.11"
  architectures    = ["x86_64"]
  # architectures    = ["arm64"]

  # # Pandas lambda layer
  # layers = ["arn:aws:lambda:us-west-1:336392948345:layer:AWSSDKPandas-Python311:4"]
  # # layers = ["arn:aws:lambda:us-west-1:336392948345:layer:AWSSDKPandas-Python39:14"]

  # timeout in seconds
  timeout         = 750

  # memory in MB
  memory_size     = 256

  # Only allow for a maximum of 8 Lambdas to be run concurrently
  reserved_concurrent_executions = 8
  
  # Attach the Lambda function to the CloudWatch Logs group
  environment {
    variables = {
        CW_LOG_GROUP         = aws_cloudwatch_log_group.recipes_scraper_lambda_log_group.name,
        OUTPUT_S3_BUCKET     = aws_s3_bucket.stage_s3_bucket.bucket,
        SCRAPE_OPS_API_KEY   = var.scrape_ops_api_key,
        DYNAMODB_TABLE       = aws_dynamodb_table.recipe_scraper_table.name,
        BRIGHT_DATA_USERNAME = var.bright_data_username,
        BRIGHT_DATA_PASSWORD = var.bright_data_password,
        BRIGHT_DATA_HOST     = var.bright_data_host,
        BRIGHT_DATA_PORT     = var.bright_data_port,
    }
  }

  depends_on = [
    aws_s3_bucket.lambda_s3_bucket,
    aws_s3_object.recipes_scraper_lambda_code_object,
    # aws_s3_bucket_notification.raw_s3_bucket_notification,
    aws_iam_role_policy_attachment.lambda_logs_policy_attachment,
    aws_cloudwatch_log_group.recipes_scraper_lambda_log_group,
    aws_s3_bucket.stage_s3_bucket,
  ]
  
  tags = {
    name              = local.name_tag
    resource_category = "lambda"
  }
}

# # Allow S3 to invoke the Lambda function
# resource "aws_lambda_permission" "allow_s3_invoke" {
#   statement_id  = "AllowS3Invoke"
#   action        = "lambda:InvokeFunction"
#   function_name = "${aws_lambda_function.recipes_scraper_lambda_function.arn}"
#   principal = "s3.amazonaws.com"
#   source_arn = "${aws_s3_bucket.raw_s3_bucket.arn}"
# }


######################################################################################
# Lambda SQS Event Source Mapping (map recipe scraper lambda to to_scrape SQS queue) #
######################################################################################

# Lambda SQS Event Source Mapping
resource "aws_lambda_event_source_mapping" "recipes_scraper_lambda_sqs_event_source_mapping" {
  event_source_arn = aws_sqs_queue.sqs_to_scrape_queue.arn
  function_name    = aws_lambda_function.recipes_scraper_lambda_function.function_name
  batch_size       = 40
  maximum_batching_window_in_seconds = 20      # (max time to wait for batch to fill up)
  function_response_types = ["ReportBatchItemFailures"]
  depends_on = [
    aws_lambda_function.recipes_scraper_lambda_function,
    aws_sqs_queue.sqs_to_scrape_queue,
  ]
}

# Allow the "to scrape" SQS queue to invoke the Recipe Scraper Lambda function
resource "aws_lambda_permission" "allow_sqs_invoke_recipes_scraper_lambda" {
  statement_id  = "AllowSQSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.recipes_scraper_lambda_function.arn}"
  principal = "sqs.amazonaws.com"
  source_arn = "${aws_sqs_queue.sqs_to_scrape_queue.arn}"
}

###################################################################
# Lambda function (Extract ingredients Triggered by new scraped messages in SQS queue) #
###################################################################

# lambda function triggered when a JSON file is uploaded to the raw S3 bucket (ObjectCreated)
# Function loads the JSON data and gets more data from the URL in the JSON and
# adds to new found data to the original JSON, then uploads this to the staging bucket
resource "aws_lambda_function" "extract_ingredients_lambda_function" {

  image_uri        = "${var.lambda_ecr_repository_url}:latest"
  # image_uri        = "${data.aws_ecr_repository.lambda_ecr_repository.repository_url}:latest"
  # image_uri        = data.aws_ecr_repository.lambda_ecr_repository.repository_url
  package_type     = "Image"

  function_name    = var.extract_ingredients_lambda_function_name

  role             = aws_iam_role.recipe_pipeline_lambda_role.arn
  
  architectures    = ["x86_64"]
  # architectures    = ["arm64"]
  # handler          = "extract_ingredients_lambda.extract_ingredients_lambda.extract_ingredients_lambda"

  # timeout in seconds
  timeout         = 150

  # # memory in MB
  memory_size     = 1856

  ephemeral_storage {
    size = 5120
  }

  # Only allow for a maximum of 5 Lambdas to be run concurrently
  reserved_concurrent_executions = 5
  
  # Attach the Lambda function to the CloudWatch Logs group
  environment {
    variables = {
        CW_LOG_GROUP         = aws_cloudwatch_log_group.extract_ingredients_lambda_log_group.name,
        OUTPUT_S3_BUCKET     = data.aws_s3_bucket.output_s3_bucket.bucket,
    }
  }

  depends_on = [
    # data.aws_ecr_repository.lambda_ecr_repository,
    # aws_iam_role_policy_attachment.lambda_logs_policy_attachment,
    aws_cloudwatch_log_group.extract_ingredients_lambda_log_group,
    data.aws_s3_bucket.output_s3_bucket,
  ]
  
  tags = {
    name              = local.name_tag
    resource_category = "lambda"
  }
}

# # Allow S3 to invoke the Lambda function
# resource "aws_lambda_permission" "allow_s3_invoke" {
#   statement_id  = "AllowS3Invoke"
#   action        = "lambda:InvokeFunction"
#   function_name = "${aws_lambda_function.recipes_scraper_lambda_function.arn}"
#   principal = "s3.amazonaws.com"
#   source_arn = "${aws_s3_bucket.raw_s3_bucket.arn}"
# }


# ######################################################################################
# # Lambda SQS Event Source Mapping (map recipe scraper lambda to to_scrape SQS queue) #
# ######################################################################################

# Lambda SQS Event Source Mapping
resource "aws_lambda_event_source_mapping" "extract_ingredients_lambda_event_source_mapping" {
  event_source_arn = aws_sqs_queue.sqs_process_staged_queue.arn
  function_name    = aws_lambda_function.extract_ingredients_lambda_function.function_name
  batch_size       = 10                        # (10 messages each referencing a CSV with ~30-40 rows)
  maximum_batching_window_in_seconds = 20      # (max time to wait for batch to fill up)
  function_response_types = ["ReportBatchItemFailures"]
  depends_on = [
    aws_lambda_function.extract_ingredients_lambda_function,
    aws_sqs_queue.sqs_process_staged_queue,
  ]
}

# # Allow the "to scrape" SQS queue to invoke the Recipe Scraper Lambda function
# resource "aws_lambda_permission" "allow_sqs_invoke_recipes_scraper_lambda" {
#   statement_id  = "AllowSQSInvoke"
#   action        = "lambda:InvokeFunction"
#   function_name = "${aws_lambda_function.recipes_scraper_lambda_function.arn}"
#   principal = "sqs.amazonaws.com"
#   source_arn = "${aws_sqs_queue.sqs_to_scrape_queue.arn}"
# }

#########################################################################################################
#################################################
########### REST API Lambda Functions ###########
#################################################
#########################################################################################################

###########################
# FastAPI Lambda Function #
###########################

# lambda function to process csv file
resource "aws_lambda_function" "recipes_api_lambda" {

  s3_bucket        = aws_s3_bucket.recipes_api_lambda_bucket.bucket
  s3_key           = var.app_lambda_zip_file_name
  # s3_key           = var.recipes_api_lambda_zip_file_name
  s3_object_version = aws_s3_object.recipes_api_lambda_code.version_id
  source_code_hash = var.app_lambda_zip_file_name
  # source_code_hash = var.recipes_api_lambda_zip_file_name
  
  function_name    = var.app_lambda_function_name
  handler            = var.app_lambda_handler
  # function_name    = var.recipes_api_lambda_function_name
  # handler          = "app.main.handler"

  role             = aws_iam_role.recipes_api_lambda_role.arn
  runtime          = "python3.11"
  architectures    = ["x86_64"]
  # architectures    = ["arm64"]
  # layers = [aws_lambda_layer_version.psychopg2_layer.arn]

  # Attach the Lambda function to the CloudWatch Logs group
  environment {
    variables = {
      CW_LOG_GROUP = aws_cloudwatch_log_group.recipe_api_log_group.name,
      # DATABASE_URL = var.db_host,
      # DATABASE_HOST = var.db_host,
      DATABASE_URL = aws_instance.ec2_db_instance.public_dns,
      DATABASE_HOST = aws_instance.ec2_db_instance.public_dns,
      DATABASE_USER = var.db_username_lambda,
      DATABASE_PW = var.db_password,
      DATABASE_PORT = var.db_port,
      DATABASE_NAME = var.db_name,
    }

  }

  # configure VPC settings so Lambda can connect with EC2 postgres DB in same VPC
  vpc_config {
    subnet_ids         = [data.aws_subnet.default_subnet1.id, data.aws_subnet.default_subnet2.id]
    # security_group_ids = [data.aws_security_group.lambda_sg.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
  
  # timeout in seconds
  timeout         = 180
  
  depends_on = [
    aws_instance.ec2_db_instance,
    aws_security_group.lambda_sg,
    aws_s3_bucket.recipes_api_lambda_bucket,
    aws_s3_object.recipes_api_lambda_code,
    # aws_s3_bucket.dish_api_lambda_bucket,
    # aws_s3_object.dish_api_lambda_code,
    aws_iam_role_policy_attachment.recipes_api_lambda_logs,
    aws_cloudwatch_log_group.recipe_api_log_group,
  ]

}

##########################################
# Lambda resource policy for API Gateway #
##########################################

# Lambda resource policy for API Gateway
resource "aws_lambda_permission" "lambda_api_gw_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.recipes_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  # source_arn = "${aws_api_gateway_rest_api.recipes_rest_api.execution_arn}/*/*/*"
  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${var.aws_account_number}:${aws_api_gateway_rest_api.recipes_rest_api.id}/*/*/*"
  # source_arn = "arn:aws:execute-api:${var.aws_region}:${var.aws_account_number}:${aws_api_gateway_rest_api.recipes_rest_api.id}/*/${aws_api_gateway_method.recipe_api_any_method.http_method}${aws_api_gateway_resource.recipe_resource.path}"

}