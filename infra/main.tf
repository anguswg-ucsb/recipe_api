terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # version = "~> 4.0"
    }
  }
}

# cloud provider
provider "aws" {
  region = var.region
  profile = var.profile
}

#################
# Local variables
#################

locals {
  csv_file_path = "/Users/anguswatters/Desktop/recipes_data/dish_recipes2.csv"
  unique_ingred_file_path = "/Users/anguswatters/Desktop/recipes_data/unique_ingredients.csv"
  # csv_file_path = "data/dish_recipes2.csv"
  # unique_ingred_file_path = "data/unique_ingredients.csv"
  # process_csv_lambda_path = "lambda/process_csv_lambda.zip"
  # s3_to_db_lambda_path = "lambda/s3_to_db.zip"
  # create_user_lambda_path = "lambda/create_user.zip"
  # psychopg2_zip_path ="lambda/psycopg2-py38.zip"
  api_lambda_zip = "../deploy/lambda_function.zip"
}

####################
# VPC and Subnet IDs
####################

data "aws_vpc" "main_vpc" {
  id = var.vpc_id
  # id = "vpc-06a9576a46a4e4979"
}

# Default VPC subnet 1 data block
data "aws_subnet" "default_subnet1" {
  id = var.subnet_id1
}

# Default VPC subnet 1 data block
data "aws_subnet" "default_subnet2" {
  id = var.subnet_id2
}

# # ##############################
# # # SECRETS MANAGERS RDS PROXY #
# # ##############################

resource "aws_secretsmanager_secret" "ec2_db_secret" {
  name_prefix = var.ec2_secret_prefix
  recovery_window_in_days = 0
  description = "Secret for EC2 DB instance"
}

# # aws_rds_cluster.aurora_dish_recipes_cluster.iam_database_authentication_enabled
# # aws_rds_cluster_instance.aurora_dish_recipes_instance
resource "aws_secretsmanager_secret_version" "ec2_secret_version" {
  secret_id     = aws_secretsmanager_secret.ec2_db_secret.id
  secret_string = jsonencode({
    "username"             = var.db_username
    "password"             = var.db_password
    "db_name"              = var.db_name
    "engine"               = "postgres"
    "port"                 = 5432
  })
}

# ###############################
# EC2 instance to run PostgresSQL
# ###############################

resource "aws_instance" "ec2_db_instance" {
  ami           = var.ec2_t2_micro_ami_id
  instance_type = "t2.micro"
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
  key_name      = aws_key_pair.ssh_key.key_name
  
  user_data_base64  = base64encode("${templatefile("${var.path_to_setup_db_script}", {
      DB_USERNAME   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["username"],
      DB_PASSWORD   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["password"],
      DB_NAME       = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["db_name"],
      S3_BUCKET     = var.s3_bucket_name,
      S3_FILE       = var.s3_csv_file_name,
      S3_UNIQUE_INGREDS_FILE = var.s3_unique_ingred_file_name,
      AWS_REGION    = var.region,
  })}")

  # user_data     = file("path/to/your/user-data-script.sh")
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  subnet_id         = data.aws_subnet.default_subnet1.id
  
  associate_public_ip_address = true

  depends_on = [
    aws_s3_bucket.dish_recipes_bucket,
    aws_s3_object.dish_recipes_bucket_object,
    aws_s3_object.uingredients_bucket_object,
    aws_secretsmanager_secret_version.ec2_secret_version,
    aws_secretsmanager_secret.ec2_db_secret
    # aws_security_group.ec2_sg,
  ]

  tags = {
    Name = "EC2 Database Instance"
  }
}

# ################
# # EC2 Elastic IP
# ################

# # Create an Elastic IP
# resource "aws_eip" "ec2_db_eip" {
#   instance = aws_instance.ec2_db_instance.id
#   # vpc      = true
#   domain  = "vpc"
#   tags = {
#     name = "Elastic IP for EC2 running postgresql for dishes project"
#   }
# }

# # Associate the Elastic IP to the instance
# resource "aws_eip_association" "ec2_db_eip_association" {
#   instance_id   = aws_instance.ec2_db_instance.id
#   allocation_id = aws_eip.ec2_db_eip.id
# }

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

resource "aws_iam_role_policy_attachment" "ec2_role_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-instance-profile"

  role = aws_iam_role.ec2_role.id
}
# # ##############
# # EC2 Key Pair #
# # ##############

# Public key to use to login to the EC2 instance
resource "aws_key_pair" "ssh_key" {
  key_name   = "ec2_db_key"
  public_key = file(var.ec2_public_key_path)
}

#################
# SECURITY GROUPS
#################

# Security group for the EC2 instance
resource "aws_security_group" "ec2_sg" {
  name        = "ec2_sg"
  description = "Security group for the EC2 Postgres DB instance"
  vpc_id      = data.aws_vpc.main_vpc.id

  # Rule to allow SSH (port 22) access from your personal IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.env_ip}/32"]
  }

  # Rule to allow PostgreSQL (port 5432) access from your personal IP
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${var.env_ip}/32"]
  }

  # # Rule to allow traffic from the Lambda security group
  ingress {
    from_port         = 5432
    to_port           = 5432
    protocol          = "tcp"
    # security_groups   = [data.aws_security_group.lambda_sg.id]
    security_groups   = [aws_security_group.lambda_sg.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ec2_sg"
  }

  depends_on = [
    # aws_instance.ec2_db_instance,
    aws_security_group.lambda_sg
  ]
}

# data "aws_security_group" "lambda_sg" {
#   id = var.lambda_sg_id
# }

#resource "aws_security_group" "lambda_sg" {
#    name = var.lambda_sg_name
#    vpc_id      = data.aws_vpc.main_vpc.id
#
#    # ingress {
#    #     from_port = 80
#    #     to_port = 80
#    #     protocol = "tcp"
#    #     cidr_blocks = ["0.0.0.0/0"]
#    # }
#
#    egress {
#        from_port = 0
#        to_port = 0
#        protocol = "-1"
#        cidr_blocks = ["0.0.0.0/0"]
#    }
#
#
#}


# #######################################
# # AWS S3 bucket (dish-recipes-bucket) #
# #######################################

# s3 bucket to store csv file
resource "aws_s3_bucket" "dish_recipes_bucket" {
  bucket = "dish-recipes-bucket"
  #   depends_on = [
  #   aws_lambda_function.s3_to_db_lambda,
  #   aws_instance.ec2_db_instance,
  # ]
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "dish_s3_bucket_ownership_controls" {
  bucket = aws_s3_bucket.dish_recipes_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "dish_s3_public_access_block" {
  bucket = aws_s3_bucket.dish_recipes_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_acl" "dish_s3_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.dish_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.dish_s3_public_access_block,
  ]

  bucket = aws_s3_bucket.dish_recipes_bucket.id
  acl    = "private"
}

data "aws_iam_policy_document" "s3_bucket_policy_document" {
  statement {
    sid = "AllowCurrentAccount"
    effect = "Allow"

    principals {
      type = "AWS"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.dish_recipes_bucket.arn,
      "${aws_s3_bucket.dish_recipes_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "aws:PrincipalAccount"
      values = [var.account_number]
    }
  }
}

# s3 bucket policy to allow public access
resource "aws_s3_bucket_policy" "dish_recipes_bucket_policy" {
  bucket = aws_s3_bucket.dish_recipes_bucket.id
  policy = data.aws_iam_policy_document.s3_bucket_policy_document.json
  depends_on = [
    aws_s3_bucket_acl.dish_s3_bucket_acl,
    aws_s3_bucket_ownership_controls.dish_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.dish_s3_public_access_block,
  ]
}
# ###############################
# # AWS S3 Object (CSV file) #
# ###############################

# s3 object to store main dish recipes CSV file
resource "aws_s3_object" "dish_recipes_bucket_object" {
  bucket = aws_s3_bucket.dish_recipes_bucket.bucket
  key    = var.s3_csv_file_name
  source = local.csv_file_path
  # depends_on = [
  #   aws_s3_bucket_notification.s3_bucket_notification,
  #   aws_lambda_function.s3_to_db_lambda,
  #   aws_instance.ec2_db_instance,
  # ]
}

# s3 object to store unique ingredients CSV file
resource "aws_s3_object" "uingredients_bucket_object" {
  bucket = aws_s3_bucket.dish_recipes_bucket.bucket
  key    = var.s3_unique_ingred_file_name
  source = local.unique_ingred_file_path
  # depends_on = [
  #   aws_s3_bucket_notification.s3_bucket_notification,
  #   aws_lambda_function.s3_to_db_lambda,
  #   aws_instance.ec2_db_instance,
  # ]
}



# ####################################################
# # AWS S3 logging bucket (dish-recipes-bucket logs) #
# ####################################################

# create s3 bucket for storing logs for dish recipes bucket
resource "aws_s3_bucket" "dish_recipes_log_bucket" {
  bucket = "dish-recipes-log-bucket"
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "dish_logs_bucket_ownership_controls" {
  bucket = aws_s3_bucket.dish_recipes_log_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "dish_logs_public_access_block" {
  bucket = aws_s3_bucket.dish_recipes_log_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# add logging bucket acl
resource "aws_s3_bucket_acl" "dish_recipes_log_bucket_acl" {

  depends_on = [
    aws_s3_bucket_ownership_controls.dish_logs_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.dish_logs_public_access_block,
  ]

  bucket = aws_s3_bucket.dish_recipes_log_bucket.id
  acl    = "log-delivery-write"
}

# add logging bucket policy to log from dish recipes bucket to dish_recipes_log_bucket 
resource "aws_s3_bucket_logging" "dish_recipes_logging" {
  bucket = aws_s3_bucket.dish_recipes_bucket.id
  target_bucket = aws_s3_bucket.dish_recipes_log_bucket.id
  target_prefix = "log/"
}

###################################
# Upload FastAPI Lambda zip to S3 #
###################################

# s3 bucket for lambda code
resource "aws_s3_bucket" "dish_api_lambda_bucket" {
  bucket = var.dish_api_bucket_name
}

# s3 object for lambda code
resource "aws_s3_object" "dish_api_lambda_code" {
  bucket = aws_s3_bucket.dish_api_lambda_bucket.bucket
  key    = "lambda_function.zip"
  source = local.api_lambda_zip
}

##################################
# FastAPI Lambda Role and Policy #
##################################

# lambda role to assume
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
resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Attach necessary policies to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_role_attachment" {
  role      = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  # policy_arn = aws_iam_policy.lambda_policy.arn
}

############################
# FastAPI Lambda Log Group #
############################

# lambda log group
resource "aws_cloudwatch_log_group" "dish_api_log_group" {
  name              = "/aws/lambda/${var.dish_api_lambda_function_name}"
  retention_in_days = 14
}

resource "aws_iam_policy" "dish_api_logging_policy" {
  name   = "dish-api-logging-policy"
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
resource "aws_iam_role_policy_attachment" "dish_api_lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dish_api_logging_policy.arn
}

###########################
# FastAPI Lambda Function #
###########################

# lambda function to process csv file
resource "aws_lambda_function" "dish_api_lambda" {
  s3_bucket        = aws_s3_bucket.dish_api_lambda_bucket.bucket
  s3_key           = "lambda_function.zip"
  function_name    = var.dish_api_lambda_function_name
  handler          = "app.main.handler"
  # handler          = "function.name/handler.process_csv_lambda"
  role             = aws_iam_role.lambda_role.arn
  runtime          = "python3.11"
  architectures    = ["x86_64"]
  # architectures    = ["arm64"]
  # layers = [aws_lambda_layer_version.psychopg2_layer.arn]

  # Attach the Lambda function to the CloudWatch Logs group
  environment {
    variables = {
      CW_LOG_GROUP = aws_cloudwatch_log_group.dish_api_log_group.name,
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
    aws_s3_bucket.dish_api_lambda_bucket,
    aws_s3_object.dish_api_lambda_code,
    aws_iam_role_policy_attachment.dish_api_lambda_logs,
    aws_cloudwatch_log_group.dish_api_log_group,
  ]

}

resource "aws_security_group" "lambda_sg" {
    name = var.lambda_sg_name
    vpc_id      = data.aws_vpc.main_vpc.id

    # ingress {
    #     from_port = 80
    #     to_port = 80
    #     protocol = "tcp"
    #     cidr_blocks = ["0.0.0.0/0"]
    # }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

  lifecycle {
    create_before_destroy = true
  }

}

# read in already made security group for lambda to connect with EC2
#data "aws_security_group" "lambda_sg" {
#  # id = var.lambda_sg_id
#  name = var.lambda_sg_name
# }
