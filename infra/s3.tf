
#######################################
# S3 bucket for raw recipes JSON data #
#######################################

# s3 bucket for raw data
resource "aws_s3_bucket" "raw_s3_bucket" {
  bucket = var.raw_s3_bucket_name
}

###############################
# S3 bucket permissions (RAW) #
###############################

# Enable object versioning on RAW S3 bucket
resource "aws_s3_bucket_versioning" "raw_s3_bucket_versioning" {
  bucket = aws_s3_bucket.raw_s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "raw_s3_bucket_ownership_controls" {
  bucket = aws_s3_bucket.raw_s3_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "raw_s3_public_access_block" {
  bucket = aws_s3_bucket.raw_s3_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_acl" "raw_s3_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.raw_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.raw_s3_public_access_block,
  ]

  bucket = aws_s3_bucket.raw_s3_bucket.id
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
      aws_s3_bucket.raw_s3_bucket.arn,
      "${aws_s3_bucket.raw_s3_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "aws:PrincipalAccount"
      values = [var.aws_account_number]
    }
  }
}

# s3 bucket policy to allow public access
resource "aws_s3_bucket_policy" "raw_bucket_policy" {
  bucket = aws_s3_bucket.raw_s3_bucket.id
  policy = data.aws_iam_policy_document.s3_bucket_policy_document.json
  depends_on = [
    aws_s3_bucket_acl.raw_s3_bucket_acl,
    aws_s3_bucket_ownership_controls.raw_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.raw_s3_public_access_block,
  ]
}


# # S3 event notification for raw data bucket to trigger lambda function
# resource "aws_s3_bucket_notification" "raw_s3_bucket_notification" {
#   bucket = aws_s3_bucket.raw_s3_bucket.id

#   lambda_function {
#     lambda_function_arn = aws_lambda_function.recipes_scraper_lambda_function.arn
#     events              = ["s3:ObjectCreated:*"]
#     # filter_prefix       = "raw/"
#     filter_suffix       = ".json"
#   }
# }

#####################
# S3 bucket (STAGE) #
#####################

# s3 bucket for raw data
resource "aws_s3_bucket" "stage_s3_bucket" {
  bucket = var.stage_s3_bucket_name
}

#################################
# S3 bucket permissions (STAGE) #
#################################

# Enable object versioning on STAGE S3 bucket
resource "aws_s3_bucket_versioning" "stage_s3_bucket_versioning" {
  bucket = aws_s3_bucket.stage_s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "stage_s3_bucket_ownership_controls" {
  bucket = aws_s3_bucket.stage_s3_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "stage_s3_public_access_block" {
  bucket = aws_s3_bucket.stage_s3_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "stage_s3_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.stage_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.stage_s3_public_access_block,
  ]

  bucket = aws_s3_bucket.stage_s3_bucket.id
  acl    = "private"
}

data "aws_iam_policy_document" "stage_s3_bucket_policy_document" {
  statement {
    sid = "RecipesStageBucketPolicyFromCurrentAccount"
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
      aws_s3_bucket.stage_s3_bucket.arn,
      "${aws_s3_bucket.stage_s3_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "aws:PrincipalAccount"
      values = [var.aws_account_number]
    }
  }
}

# s3 bucket policy to allow public access
resource "aws_s3_bucket_policy" "stage_bucket_policy" {
  bucket = aws_s3_bucket.stage_s3_bucket.id
  policy = data.aws_iam_policy_document.stage_s3_bucket_policy_document.json
  depends_on = [
    aws_s3_bucket_acl.stage_s3_bucket_acl,
    aws_s3_bucket_ownership_controls.stage_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.stage_s3_public_access_block,
  ]
}

###############################
# S3 bucket for lambda function code #
###############################

# s3 bucket for lambda code
resource "aws_s3_bucket" "lambda_s3_bucket" {
  bucket = var.lambda_s3_bucket_name
}

# S3 object for Lambda function code for chunking uploaded CSV files and sending into SQS queue
resource "aws_s3_object" "chunk_csv_lambda_code_object" {
  bucket = aws_s3_bucket.lambda_s3_bucket.bucket
  key    = var.chunk_csv_lambda_zip_file_name
  source = local.chunk_csv_zip
  etag   = filemd5(local.chunk_csv_zip)
}

# S3 object for Lambda function code for chunking uploaded CSV files and sending into SQS queue
resource "aws_s3_object" "csv_to_json_lambda_code_object" {
  bucket = aws_s3_bucket.lambda_s3_bucket.bucket
  key    = var.csv_to_json_lambda_zip_file_name
  source = local.csv_to_json_zip
  etag   = filemd5(local.csv_to_json_zip)
}

# S3 object for Lambda function code for consuming SQS queue and scraping internet for recipes and storing in S3 bucket
resource "aws_s3_object" "recipes_scraper_lambda_code_object" {
  bucket = aws_s3_bucket.lambda_s3_bucket.bucket
  key    = var.recipes_scraper_lambda_zip_file_name
  source = local.recipes_scraper_zip
  etag   = filemd5(local.recipes_scraper_zip)
}

# ####################################
# # AWS S3 bucket (OUTPUT S3 BUCKET) #
# ####################################

# s3 bucket for raw data
data "aws_s3_bucket" "output_s3_bucket" {
  bucket = var.output_s3_bucket_name
}

# # s3 bucket to store csv file
# resource "aws_s3_bucket" "output_s3_bucket" {
#   bucket = "dish-recipes-bucket"
#   #   depends_on = [
#   #   aws_lambda_function.s3_to_db_lambda,
#   #   aws_instance.ec2_db_instance,
#   # ]
# }

#######################################
# S3 bucket permissions (Output CSVs) #
#######################################

# Enable object versioning on RAW S3 bucket
resource "aws_s3_bucket_versioning" "output_s3_bucket_versioning" {
  bucket = data.aws_s3_bucket.output_s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "output_s3_bucket_ownership_controls" {
  bucket = data.aws_s3_bucket.output_s3_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "output_s3_public_access_block" {
  bucket = data.aws_s3_bucket.output_s3_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_acl" "output_s3_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.output_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.output_s3_public_access_block,
  ]

  bucket = data.aws_s3_bucket.output_s3_bucket.id
  acl    = "private"
}

data "aws_iam_policy_document" "output_s3_bucket_policy_document" {
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
      data.aws_s3_bucket.output_s3_bucket.arn,
      "${data.aws_s3_bucket.output_s3_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "aws:PrincipalAccount"
      values = [var.aws_account_number]
    }
  }
}

# s3 bucket policy to allow public access
resource "aws_s3_bucket_policy" "output_bucket_policy" {
  bucket = data.aws_s3_bucket.output_s3_bucket.id
  policy = data.aws_iam_policy_document.output_s3_bucket_policy_document.json
  depends_on = [
    aws_s3_bucket_acl.output_s3_bucket_acl,
    aws_s3_bucket_ownership_controls.output_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.output_s3_public_access_block,
  ]
}

# ####################################
# # AWS S3 bucket (database backup S3 bucket) #
# ####################################

# s3 bucket for raw data
data "aws_s3_bucket" "backup_s3_bucket" {
  bucket = var.backup_s3_bucket_name
}

# # s3 bucket to store csv file
# resource "aws_s3_bucket" "backup_s3_bucket" {
#   bucket = "dish-recipes-bucket"
#   #   depends_on = [
#   #   aws_lambda_function.s3_to_db_lambda,
#   #   aws_instance.ec2_db_instance,
#   # ]
# }

#######################################
# S3 bucket permissions (database backup S3 bucket) #
#######################################

# Enable object versioning on RAW S3 bucket
resource "aws_s3_bucket_versioning" "backup_s3_bucket_versioning" {
  bucket = data.aws_s3_bucket.backup_s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "backup_s3_bucket_ownership_controls" {
  bucket = data.aws_s3_bucket.backup_s3_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "backup_s3_public_access_block" {
  bucket = data.aws_s3_bucket.backup_s3_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_acl" "backup_s3_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.backup_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.backup_s3_public_access_block,
  ]

  bucket = data.aws_s3_bucket.backup_s3_bucket.id
  acl    = "private"
}

data "aws_iam_policy_document" "backup_s3_bucket_policy_document" {
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
      data.aws_s3_bucket.backup_s3_bucket.arn,
      "${data.aws_s3_bucket.backup_s3_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "aws:PrincipalAccount"
      values = [var.aws_account_number]
    }
  }
}

# s3 bucket policy to allow public access
resource "aws_s3_bucket_policy" "backup_bucket_policy" {
  bucket = data.aws_s3_bucket.backup_s3_bucket.id
  policy = data.aws_iam_policy_document.backup_s3_bucket_policy_document.json
  depends_on = [
    aws_s3_bucket_acl.backup_s3_bucket_acl,
    aws_s3_bucket_ownership_controls.backup_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.backup_s3_public_access_block,
  ]
}

# -----------------------------------------------
# # AWS S3 bucket (contains scripts run on EC2) #
# -----------------------------------------------

# s3 bucket for raw data
resource "aws_s3_bucket" "script_bucket" {
  bucket = var.recipes_db_scripts_bucket_name
}

# S3 object for SQS consumer python script that runs on EC2 instance
resource "aws_s3_object" "script_bucket_object" {
  bucket = aws_s3_bucket.script_bucket.id
  key    = var.recipes_consumer_script_filename
  source = local.recipe_script_path
  etag   = filemd5(local.recipe_script_path)
}

# S3 object for bash script that runs on EC2 instance to backup recipes database
resource "aws_s3_object" "backup_script_bucket_object" {
  bucket = aws_s3_bucket.script_bucket.id
  key    = var.recipes_backup_script_filename
  source = local.recipe_backup_script_path
  etag   = filemd5(local.recipe_backup_script_path)
}

# S3 object for bash script that runs on EC2 instance to restore database from S3 backup 
resource "aws_s3_object" "restore_script_bucket_object" {
  bucket = aws_s3_bucket.script_bucket.id
  key    = var.recipes_restore_script_filename
  source = local.recipe_restore_script_path
  etag   = filemd5(local.recipe_restore_script_path)
}

# -------------------------------------
# S3 bucket permissions (EC2 scripts) #
# -------------------------------------

# Enable object versioning on STAGE S3 bucket
resource "aws_s3_bucket_versioning" "script_s3_bucket_versioning" {
  bucket = aws_s3_bucket.script_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "script_s3_bucket_ownership_controls" {
  bucket = aws_s3_bucket.script_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "script_s3_public_access_block" {
  bucket = aws_s3_bucket.script_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "script_s3_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.script_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.script_s3_public_access_block,
  ]

  bucket = aws_s3_bucket.script_bucket.id
  acl    = "private"
}

data "aws_iam_policy_document" "script_s3_bucket_policy_document" {
  statement {
    sid = "RecipesScriptsBucketPolicyFromCurrentAccount"
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
      aws_s3_bucket.script_bucket.arn,
      "${aws_s3_bucket.script_bucket.arn}/*"
    ]

    condition {
      test = "StringEquals"
      variable = "aws:PrincipalAccount"
      values = [var.aws_account_number]
    }
  }
}

# s3 bucket policy to allow public access
resource "aws_s3_bucket_policy" "script_bucket_policy" {
  bucket = aws_s3_bucket.script_bucket.id
  policy = data.aws_iam_policy_document.script_s3_bucket_policy_document.json
  depends_on = [
    aws_s3_bucket_acl.script_s3_bucket_acl,
    aws_s3_bucket_ownership_controls.script_s3_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.script_s3_public_access_block,
  ]
}


# # ##########################################
# # # AWS S3 Object (Upload local CSV files) #
# # ##########################################

# # s3 object to store main dish recipes CSV file
# resource "aws_s3_object" "output_s3_bucket_object" {
#   bucket = data.aws_s3_bucket.output_s3_bucket.bucket
#   key    = var.s3_csv_file_name
#   source = local.csv_file_path
#   # depends_on = [
#   #   aws_s3_bucket_notification.s3_bucket_notification,
#   #   aws_lambda_function.s3_to_db_lambda,
#   #   aws_instance.ec2_db_instance,
#   # ]
# }

# # s3 object to store unique ingredients CSV file
# resource "aws_s3_object" "uingredients_bucket_object" {
#   bucket = data.aws_s3_bucket.output_s3_bucket.bucket
#   key    = var.s3_unique_ingred_file_name
#   source = local.unique_ingred_file_path
#   # depends_on = [
#   #   aws_s3_bucket_notification.s3_bucket_notification,
#   #   aws_lambda_function.s3_to_db_lambda,
#   #   aws_instance.ec2_db_instance,
#   # ]
# }

# ###########################################################
# # AWS S3 logging bucket (Logging bucketg for OUTPUT CSVs) #
# ###########################################################

# create s3 bucket for storing logs for dish recipes bucket
resource "aws_s3_bucket" "output_recipes_log_bucket" {
  bucket = var.output_recipes_log_bucket_name
}

# s3 bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "output_recipes_bucket_ownership_controls" {
  bucket = aws_s3_bucket.output_recipes_log_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
# s3 bucket public access block
resource "aws_s3_bucket_public_access_block" "output_recipes_logs_public_access_block" {
  bucket = aws_s3_bucket.output_recipes_log_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# add logging bucket acl
resource "aws_s3_bucket_acl" "output_recipes_log_bucket_acl" {

  depends_on = [
    aws_s3_bucket_ownership_controls.output_recipes_bucket_ownership_controls,
    aws_s3_bucket_public_access_block.output_recipes_logs_public_access_block,
  ]

  bucket = aws_s3_bucket.output_recipes_log_bucket.id
  acl    = "log-delivery-write"
}

# add logging bucket policy to log from dish recipes bucket to output_recipes_log_bucket 
resource "aws_s3_bucket_logging" "output_recipes_logging" {
  bucket = data.aws_s3_bucket.output_s3_bucket.id
  target_bucket = aws_s3_bucket.output_recipes_log_bucket.id
  target_prefix = "log/"
}

###################################
# Upload FastAPI Lambda zip to S3 #
###################################

# s3 bucket for lambda code
resource "aws_s3_bucket" "recipe_api_lambda_bucket" {
  bucket = var.recipe_api_bucket_name
  tags = {
    name = local.name_tag
    resource_category = "s3"
  }
}

# s3 object for FAST API REST API for lambda function zip file
resource "aws_s3_object" "recipe_api_lambda_code" {
  bucket = aws_s3_bucket.recipe_api_lambda_bucket.bucket
  key    = var.app_lambda_zip_file_name
  # key    = var.recipe_api_lambda_zip_file_name
  source = local.app_zip
  etag   = filemd5(local.app_zip)
  # source_hash = filemd5(local.api_lambda_zip)
  tags = {
    name = local.name_tag
    resource_category = "s3"
  }
}


# # ####################################################
# # # AWS S3 logging bucket (dish-recipes-bucket logs) #
# # ####################################################

# # create s3 bucket for storing logs for dish recipes bucket
# resource "aws_s3_bucket" "dish_recipes_log_bucket" {
#   bucket = "dish-recipes-log-bucket"
# }

# # s3 bucket ownership controls
# resource "aws_s3_bucket_ownership_controls" "dish_logs_bucket_ownership_controls" {
#   bucket = aws_s3_bucket.dish_recipes_log_bucket.id
#   rule {
#     object_ownership = "BucketOwnerPreferred"
#   }
# }
# # s3 bucket public access block
# resource "aws_s3_bucket_public_access_block" "dish_logs_public_access_block" {
#   bucket = aws_s3_bucket.dish_recipes_log_bucket.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

# # add logging bucket acl
# resource "aws_s3_bucket_acl" "dish_recipes_log_bucket_acl" {

#   depends_on = [
#     aws_s3_bucket_ownership_controls.dish_logs_bucket_ownership_controls,
#     aws_s3_bucket_public_access_block.dish_logs_public_access_block,
#   ]

#   bucket = aws_s3_bucket.dish_recipes_log_bucket.id
#   acl    = "log-delivery-write"
# }

# # add logging bucket policy to log from dish recipes bucket to dish_recipes_log_bucket 
# resource "aws_s3_bucket_logging" "dish_recipes_logging" {
#   bucket = aws_s3_bucket.output_s3_bucket.id
#   target_bucket = aws_s3_bucket.dish_recipes_log_bucket.id
#   target_prefix = "log/"
# }