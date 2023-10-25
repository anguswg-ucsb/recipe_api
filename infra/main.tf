terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

# cloud provider
provider "aws" {
  region = var.region
  profile = var.profile
}

# Local files to upload to S3
locals {
  api_lambda_zip = "../deploy/lambda_function.zip"
}

####################
# VPC and Subnet IDs
####################

data "aws_vpc" "main_vpc" {
  id = var.vpc_id
}
# Default VPC subnet 1 data block
data "aws_subnet" "default_subnet1" {
  id = var.subnet_id1
}

# Default VPC subnet 1 data block
data "aws_subnet" "default_subnet2" {
  id = var.subnet_id2
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

# # Create an IAM policy for the lambda to access S3 and DynamoDB
# resource "aws_iam_policy" "lambda_policy" {
#   name = "lambda_policy"

#   policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Allow",
#       "Action": "s3:GetObject",
#       "Resource": "arn:aws:s3:::dish-recipes-bucket/*"
#     },
#     {
#       "Effect": "Allow",
#       "Action": [
#         "logs:CreateLogGroup",
#         "logs:CreateLogStream",
#         "logs:PutLogEvents",
#         "ec2:CreateNetworkInterface",
#         "ec2:DescribeNetworkInterfaces",
#         "ec2:DeleteNetworkInterface",
#         "ec2:AssignPrivateIpAddresses",
#         "ec2:UnassignPrivateIpAddresses",
#         "rds-db:*"
#         ],
#       "Resource": "*"
#     }
#   ]
# }
# EOF
# }

# resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
#     role       = aws_iam_role.lambda.name
#     policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
# }

# arn:aws:iam::aws:policy/AWSLambda_FullAccess
# arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

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
      DATABASE_URL = var.db_host,
      DATABASE_HOST = var.db_host,
      DATABASE_USER = var.db_username,
      DATABASE_PW = var.db_password,
      DATABASE_PORT = var.db_port,
      DATABASE_NAME = var.db_name,
    }

  }

  # configure VPC settings so Lambda can connect with EC2 postgres DB in same VPC
  vpc_config {
    subnet_ids         = [data.aws_subnet.default_subnet1.id, data.aws_subnet.default_subnet2.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
  
  # timeout in seconds
  timeout         = 900
  
  depends_on = [
    aws_s3_bucket.dish_api_lambda_bucket,
    aws_s3_object.dish_api_lambda_code,
    aws_iam_role_policy_attachment.dish_api_lambda_logs,
    aws_cloudwatch_log_group.dish_api_log_group,
  ]

}
resource "aws_security_group" "lambda_sg" {
    name = "lambda-sg"
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


}

# resource "aws_security_group" "sg_lambda" {
#   name = "sg-lambda"
#   vpc_id      = data.aws_vpc.main_vpc.id

#   egress {
#     from_port        = 0
#     to_port          = 0
#     protocol         = "-1"
#     cidr_blocks      = ["0.0.0.0/0"]
#   }
# }

# resource "aws_security_group" "sg_rds_proxy" {
#   vpc_id      = data.aws_vpc.main_vpc.id

#   ingress {
#     description      = "POSTGRES TLS from sg_lambda"
#     from_port        = 5432
#     to_port          = 5432
#     protocol         = "tcp"
#     security_groups  = [aws_security_group.sg_lambda.id]
#   }

#   egress {
#     from_port        = 0
#     to_port          = 0
#     protocol         = "-1"
#     cidr_blocks      = ["0.0.0.0/0"]
#   }
# }

# resource "aws_security_group" "sg_rds" {
#   vpc_id      = data.aws_vpc.main_vpc.id

#   ingress {
#     description      = "POSTGRES TLS from sg_rds_proxy"
#     from_port        = 5432
#     to_port          = 5432
#     protocol         = "tcp"
#     security_groups  = [aws_security_group.sg_rds_proxy.id]
#   }

#   egress {
#     from_port        = 0
#     to_port          = 0
#     protocol         = "-1"
#     cidr_blocks      = ["0.0.0.0/0"]
#   }
# }

# ##################################
# # RDS PROXY PERMISSION ASSUME ROLE
# ##################################

# data "aws_iam_policy_document" "assume_role" {

#   statement {
#     effect  = "Allow"
#     actions = ["sts:AssumeRole"]

#     principals {
#       type        = "Service"
#       identifiers = ["rds.amazonaws.com"]
#     }
#   }
# }

# data "aws_iam_policy_document" "rds_proxy_policy_document" {

#   statement {
#     sid = "AllowProxyToGetDbCredsFromSecretsManager"

#     actions = [
#       "secretsmanager:GetSecretValue"
#     ]

#     resources = [
#       aws_secretsmanager_secret.rds_secret.arn
#     ]
#   }

#   statement {
#     sid = "AllowProxyToDecryptDbCredsFromSecretsManager"

#     actions = [
#       "kms:Decrypt"
#     ]

#     resources = [
#       "*"
#     ]

#     condition {
#       test     = "StringEquals"
#       values   = ["secretsmanager.${var.my_aws_region}.amazonaws.com"]
#       variable = "kms:ViaService"
#     }
#   }
# }

# resource "aws_iam_policy" "rds_proxy_iam_policy" {
#   name   = "rds-proxy-policy"
#   policy = data.aws_iam_policy_document.rds_proxy_policy_document.json
# }

# resource "aws_iam_role_policy_attachment" "rds_proxy_iam_attach" {
#   policy_arn = aws_iam_policy.rds_proxy_iam_policy.arn
#   role       = aws_iam_role.rds_proxy_iam_role.name
# }

# resource "aws_iam_role" "rds_proxy_iam_role" {
#   name               = "rds-proxy-role"
#   assume_role_policy = data.aws_iam_policy_document.assume_role.json
# }

# data "http" "env_ip" {
#   url = "https://ipv4.icanhazip.com"
# }
# data "http" "my_public_ip" {
#   url = "https://ifconfig.co/json"
#   request_headers = {
#     Accept = "application/json"
#   }
# }

# locals {
#   ifconfig_co_json = jsondecode(data.http.my_public_ip.body)
# }

# output "my_ip_addr" {
#   value = local.ifconfig_co_json.ip
# }

# resource "aws_security_group" "aurora_sg" {
#     name = "aurora-sg"
#     vpc_id      = data.aws_vpc.main_vpc.id

#     ingress {
#         from_port = 5432
#         to_port = 5432
#         protocol = "tcp"
#         security_groups = [aws_security_group.lambda_sg.id]
#     }

#     ingress {
#       from_port = 5432
#       to_port = 5432
#       protocol = "tcp"
#       cidr_blocks = ["${var.env_ip}/32"]
#     }

#     ingress {
#       from_port = 443
#       to_port = 443
#       protocol = "tcp"
#       cidr_blocks = ["${var.env_ip}/32"]
#     }

#     ingress {
#       from_port = 22
#       to_port = 22
#       protocol = "tcp"
#       cidr_blocks = ["${var.env_ip}/32"]
#     }

#     egress {
#         from_port = 0
#         to_port = 0
#         protocol = "-1"
#         cidr_blocks = ["0.0.0.0/0"]
#     }

# }