#########################################################################################################
##############################################
########### Datapipline permissions ###########
###############################################
#########################################################################################################

#####################################
# Lambda Role (primary lambda role) #
#####################################

# IAM policy document allowing Lambda to AssumeRole
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Create an IAM role for the lambda to assume role
resource "aws_iam_role" "recipe_pipeline_lambda_role" {
  name_prefix         = "recipes_pipeline_lambda_role"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  tags = {
    name              = local.name_tag
    resource_category = "iam"
  }
}

##########################################################################################
# Lambda Role (recipe_pipeline_lambda_role) Attach AWSLambdaBasicExecutionRole Policy (AWS managed role) #
##########################################################################################

# Attach necessary policies to the IAM role
resource "aws_iam_role_policy_attachment" "recipe_pipeline_lambda_role_attachment" {
  role       = aws_iam_role.recipe_pipeline_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  # policy_arn = aws_iam_policy.lambda_policy.arn
}

###############################################################
# Lambda Role (recipe_pipeline_lambda_role) Attach S3 permissions Policy #
###############################################################

# Inline policy for S3 permissions using jsonencode
data "aws_iam_policy_document" "lambda_s3_and_sqs_policy_doc" {
  statement {
    sid = "RecipesS3AndSQSPermissionsForLambda"
    
    effect = "Allow"

    actions = [
          "s3:GetObject", 
          "s3:PutObject",
          "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.raw_s3_bucket.arn,
      "${aws_s3_bucket.raw_s3_bucket.arn}/*",
      aws_s3_bucket.stage_s3_bucket.arn,
      "${aws_s3_bucket.stage_s3_bucket.arn}/*",
    ]
  }

    statement {
    sid = "SQSReadDeletePermissions"
    
    effect = "Allow"

    actions = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
    ]

    resources = [
      aws_sqs_queue.sqs_to_scrape_queue.arn,
      aws_sqs_queue.sqs_csv_chunk_queue.arn,
      aws_sqs_queue.sqs_process_staged_queue.arn,
      ]
  }

}

# Make an IAM policy from the IAM policy document for S3/SQS permissions for sqs_consumer lambda
resource "aws_iam_policy" "lambda_s3_policy" {
  name_prefix = "recipe-lambdas-s3-and-sqs-policy"
  description = "IAM Policy for Recipes Data Pipline Lambdas to interact with S3 and SQS"
  policy      = data.aws_iam_policy_document.lambda_s3_and_sqs_policy_doc.json
  tags = {
    name              = local.name_tag
    resource_category = "iam"
  }
}

# Attach the inline S3 policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  role       = aws_iam_role.recipe_pipeline_lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

###############################################################
# Lambda Logging Policy 
# - Allow Lambda to send logs to CloudWatch Logs #
###############################################################

resource "aws_iam_policy" "logging_policy" {
  name_prefix   = "recipe-lambdas-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach the lambda logging IAM policy to the Python lambda roles
resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attachment" {
  role       = aws_iam_role.recipe_pipeline_lambda_role.name
  policy_arn = aws_iam_policy.logging_policy.arn
}

##############################
# DynamoDB Table permissions #
##############################

# Policy docuemnet for DynamoDB permissions 
data "aws_iam_policy_document" "lambda_dynamodb_policy_doc" {
  statement {
    sid = "LambdaDynamoDBPermissions"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:Query",
      "dynamodb:Scan",
    ]

    resources = [
      aws_dynamodb_table.recipe_scraper_table.arn,
      "${aws_dynamodb_table.recipe_scraper_table.arn}/*"
    ]
  }
}

# Make an IAM policy from the IAM policy document for DynamoDB permissions
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name_prefix = "recipes-lambda-dynamodb-policy"
  description = "IAM Policy for Recipes Lambda to interact with DynamoDB"
  policy      = data.aws_iam_policy_document.lambda_dynamodb_policy_doc.json
  tags = {
    name              = local.name_tag
    resource_category = "iam"
  }
}

# Attach the inline DynamoDB policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_policy_attachment" {
  role       = aws_iam_role.recipe_pipeline_lambda_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

#########################################################################################################
##############################################
##### REST API and Database permissions ######
##############################################
#########################################################################################################

##############
# EC2 IAM ROLE
##############

resource "aws_iam_role" "ec2_role" {
  name = "EC2-IAM-ReadOnly"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# add policy for EC2 to receive SQS messages
resource "aws_iam_policy" "ec2_policy" {
  name = "EC2-SQS-ReceiveMessage"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "Stmt1426528957000",
        "Effect": "Allow",
        "Action": [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        "Resource": [
          "${aws_sqs_queue.sqs_output_queue.arn}"
        ]
      }
    ]
}
EOF
}

# # add policy for EC2 to receive SQS messages AND Get/Put/List S3 objects from database backup S3 bucket
# resource "aws_iam_policy" "ec2_policy" {
#   name = "EC2-SQS-ReceiveMessage"

#   policy = <<EOF
# {
#     "Version": "2012-10-17",
#     "Statement": [
#       {
#         "Sid": "Stmt1426528957000",
#         "Effect": "Allow",
#         "Action": [
#           "sqs:ReceiveMessage",
#           "sqs:DeleteMessage",
#           "sqs:GetQueueAttributes",
#           "s3:GetObject",
#           "s3:PutObject",
#           "s3:ListBucket"
#         ],
#         "Resource": [
#           "${aws_sqs_queue.sqs_output_queue.arn}",
#           "${aws_s3_bucket.raw_s3_bucket.arn}",
#         ]
#       }
#     ]
# }
# EOF
# }

# add policy for EC2 to recieve SQS messages
resource "aws_iam_role_policy_attachment" "ec2_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_policy.arn
}

# add policy for EC2 to read from S3
resource "aws_iam_role_policy_attachment" "ec2_role_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-instance-profile"

  role = aws_iam_role.ec2_role.id
}

##################################
# FastAPI Lambda Role and Policy #
##################################

# # lambda role to assume
# data "aws_iam_policy_document" "lambda_assume_role" {
#   statement {
#     effect = "Allow"

#     principals {
#       type        = "Service"
#       identifiers = ["lambda.amazonaws.com"]
#     }

#     actions = ["sts:AssumeRole"]
#   }
# }

# Create an IAM role for the lambda to assume role
resource "aws_iam_role" "recipe_api_lambda_role" {
  name               = "recipe_api_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Attach necessary policies to the IAM role
resource "aws_iam_role_policy_attachment" "recipe_api_lambda_role_attachment" {
  role      = aws_iam_role.recipe_api_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  # policy_arn = aws_iam_policy.lambda_policy.arn
}

###################################
# FastAPI Lambda Log Group Policy #
###################################

resource "aws_iam_policy" "recipe_api_logging_policy" {
  name   = "recipe-api-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach the lambda logging IAM policy to the lambda role
resource "aws_iam_role_policy_attachment" "recipe_api_lambda_logs" {
  role       = aws_iam_role.recipe_api_lambda_role.name
  policy_arn = aws_iam_policy.recipe_api_logging_policy.arn
}

#############################
# API Gateway Role/Policies #
#############################

# Create an IAM role for API Gateway to execute and invoke the Lambda function
resource "aws_iam_role" "api_gateway_role" {
  name = "api_gateway_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      }
    }
  ]
}
EOF
}

# Attach policies to the role allowing API Gateway to execute and invoke Lambda functions
resource "aws_iam_role_policy_attachment" "api_gateway_role_policies" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
  role       = aws_iam_role.api_gateway_role.name
}

resource "aws_iam_policy" "api_gateway_invoke_policy" {
  name        = "api_gateway_invoke_policy"
  description = "Policy for API Gateway to invoke Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = aws_lambda_function.recipe_api_lambda.arn,
      },
    ],
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_invoke_role_policy_attachment" {
  policy_arn = aws_iam_policy.api_gateway_invoke_policy.arn
  role       = aws_iam_role.api_gateway_role.name
}