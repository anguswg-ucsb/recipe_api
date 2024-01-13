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
  ami           = var.ec2_t2_micro_ami_id
  instance_type = "t2.micro"
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name
  key_name      = aws_key_pair.ssh_key.key_name
  
  user_data_base64  = base64encode("${templatefile("${var.path_to_setup_ec2_script}", {
      DB_USERNAME   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["username"],
      DB_PASSWORD   = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["password"],
      DB_NAME       = jsondecode(aws_secretsmanager_secret_version.ec2_secret_version.secret_string)["db_name"],
      S3_BUCKET     = var.output_s3_bucket_name,
      # S3_FILE       = var.s3_csv_file_name,
      # S3_UNIQUE_INGREDS_FILE = var.s3_unique_ingred_file_name,
      AWS_REGION    = var.aws_region,
  })}")

  # user_data     = file("path/to/your/user-data-script.sh")
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  subnet_id         = data.aws_subnet.default_subnet1.id
  
  associate_public_ip_address = true

  depends_on = [
    data.aws_s3_bucket.output_s3_bucket,
    # aws_s3_object.output_s3_bucket_object,
    # aws_s3_object.uingredients_bucket_object,
    aws_secretsmanager_secret_version.ec2_secret_version,
    aws_secretsmanager_secret.ec2_db_secret
    # aws_security_group.ec2_sg,
  ]

  tags = {
    Name = "EC2 Database Instance"
  }
}

# Public key to use to login to the EC2 instance
resource "aws_key_pair" "ssh_key" {
  key_name   = "ec2_db_key"
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
