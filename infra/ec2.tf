# #############################################
# EC2 instance to run PostgresSQL (version 2) #
# #############################################

# Using Shell script sh/setup_ec2.sh:
# - Install PostgresSQL
# - Create a database
# - Create a recipes table with columns and a dish ID
# - DOES NOT COPY ANY DATA, INSTEAD WAITS FOR A LAMBDA FUNCTION TO BE TRIGGERED FROM A OUTPUT S3 BUCKET ObjectCreated, the lambda then 
      # copies the data into the EC2 postgres database COPY COMMAND TO COPY DATA FROM S3 BUCKET

resource "aws_instance" "ec2_db_instance" {
  ami                  = var.ec2_t2_micro_ami_id
  instance_type        = "t2.micro"
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
  key_name             = aws_key_pair.ssh_key.key_name
  
  # User data script to: 
  #  Install PostgresSQL
  #  Create a database
  #  Create a recipe_table and unique_ingredients_table with required columns
  #  Run python SQS consumer script to consume S3 events from SQS queue as new output CSV files are added to output S3 bucket 
  #  New CSVs data are downloaded from S3 and then COPIED into the EC2 postgres database
  user_data_base64  = base64encode("${templatefile("${var.path_to_setup_ec2_script}", {
      DB_USERNAME   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["username"],
      DB_PASSWORD   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["password"],
      DB_NAME       = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["db_name"],
      S3_BUCKET                  = var.output_s3_bucket_name,
      BACKUP_BUCKET              = var.backup_s3_bucket_name,
      # S3_FILE       = var.s3_csv_file_name,
      # S3_UNIQUE_INGREDS_FILE = var.s3_unique_ingred_file_name,
      # MAIN_PY_SCRIPT = data.template_file.main_py.rendered,  # Use the rendered content of main.py
      SCRIPTS_S3_BUCKET          = var.recipe_script_bucket_name,
      SQS_CONSUMER_PYTHON_SCRIPT = var.recipe_script_filename,
      BACKUP_DB_SCRIPT           = var.recipe_backup_script_filename,
      SQS_QUEUE_URL              = aws_sqs_queue.sqs_output_queue.url,
      S3_DOWNLOADS_PATH          = var.s3_downloads_path,
      BACKUO_DOWNLOADS_PATH      = var.backup_downloads_path,
      AWS_REGION                 = var.aws_region,
  })}")

  # user_data     = file("path/to/your/user-data-script.sh")
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  subnet_id              = data.aws_subnet.default_subnet1.id
  
  associate_public_ip_address = true

  depends_on = [
    data.aws_s3_bucket.output_s3_bucket, # Static S3 bucket that will contain the finalized output CSV files
    aws_s3_bucket.script_bucket,         # Bucket with SQS consumer python script
    aws_s3_object.script_bucket_object,  # SQS consumer python script
    aws_sqs_queue.sqs_output_queue,      # SQS queue that SQS consumer python script will consume from
    # aws_s3_object.output_s3_bucket_object,
    # aws_s3_object.uingredients_bucket_object,
    aws_secretsmanager_secret_version.ec2_secret_version,
    aws_secretsmanager_secret.ec2_db_secret
    # aws_security_group.ec2_sg,
  ]
  
  # replace instance if user data changes
  user_data_replace_on_change = true

  # # don't force-recreate instance if only user data changes
  # lifecycle {
  #   ignore_changes = [user_data]
  # }

  tags = {
    Name = "EC2 Database Instance"
  }
}

# # path to SQS consumer python script
# data "template_file" "main_py" {
#   template = file("${var.path_to_sqs_consumer_script}")
# }

# Public key to use to login to the EC2 instance
resource "aws_key_pair" "ssh_key" {
  key_name   = var.ec2_db_key_name
  public_key = file(var.ec2_public_key_path)
}

# #############################################
# EC2 instance to run PostgresSQL (version 1) #
# #############################################

# Using Shell script sh/setup_db.sh:
# - Install PostgresSQL
# - Create a database
# - Create a recipes table with columns and a unique ingredients table
# - COPIES specific CSV data from S3 bucket into the EC2 and then issues a COPY command to copy the data into the EC2 postgres database
# - The script then deletes the copied CSV file from the EC2 instance

# resource "aws_instance" "ec2_db_instance" {
#   ami           = var.ec2_t2_micro_ami_id
#   instance_type = "t2.micro"
#   iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
#   key_name      = aws_key_pair.ssh_key.key_name
  
#   user_data_base64  = base64encode("${templatefile("${var.path_to_setup_db_script}", {
#       DB_USERNAME   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["username"],
#       DB_PASSWORD   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["password"],
#       DB_NAME       = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["db_name"],
#       S3_BUCKET     = var.s3_bucket_name,
#       S3_FILE       = var.s3_csv_file_name,
#       S3_UNIQUE_INGREDS_FILE = var.s3_unique_ingred_file_name,
#       AWS_REGION    = var.aws_region,
#   })}")

#   # user_data     = file("path/to/your/user-data-script.sh")
#   vpc_security_group_ids = [aws_security_group.ec2_sg.id]
#   subnet_id         = data.aws_subnet.default_subnet1.id
  
#   associate_public_ip_address = true

#   depends_on = [
#     aws_s3_bucket.output_s3_bucket,
#     aws_s3_object.output_s3_bucket_object,
#     aws_s3_object.uingredients_bucket_object,
#     aws_secretsmanager_secret_version.ec2_secret_version,
#     aws_secretsmanager_secret.ec2_db_secret
#     # aws_security_group.ec2_sg,
#   ]

#   tags = {
#     Name = "EC2 Database Instance"
#   }
# }

# # Public key to use to login to the EC2 instance
# resource "aws_key_pair" "ssh_key" {
#   key_name   = "ec2_db_key"
#   public_key = file(var.ec2_public_key_path)
# }
