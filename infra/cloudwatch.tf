
#########################################################################################################
########### Data pipline CloudWatch Logs ###########
#########################################################################################################

######################################
# Lambda Log Group (chunk_csv lambda) #
######################################

# Cloudwatch log group for 'chunk_csv' Python lambda function
resource "aws_cloudwatch_log_group" "chunk_csv_lambda_log_group" {
  # name_prefix              = "/aws/lambda/${var.chunk_csv_lambda_function_name}"
  name              = "/aws/lambda/${var.chunk_csv_lambda_function_name}"
  retention_in_days = 14
  skip_destroy = false
  # skip_destroy = true
}

######################################
# Lambda Log Group (csv_to_json lambda) #
######################################

# Cloudwatch log group for 'csv_to_json' Python lambda function
resource "aws_cloudwatch_log_group" "csv_to_json_lambda_log_group" {
  # name_prefix              = "/aws/lambda/${var.csv_to_json_lambda_function_name}"
  name              = "/aws/lambda/${var.csv_to_json_lambda_function_name}"
  retention_in_days = 14
  skip_destroy = false
  # skip_destroy = true
}


######################################
# Lambda Log Group (recipes_scraper lambda) #
######################################

# Cloudwatch log group for 'recipes_scraper' Python lambda function
resource "aws_cloudwatch_log_group" "recipes_scraper_lambda_log_group" {
  # name_prefix              = "/aws/lambda/${var.recipes_scraper_lambda_function_name}"
  name             = "/aws/lambda/${var.recipes_scraper_lambda_function_name}"
  retention_in_days = 14
  skip_destroy = false
  # skip_destroy = true
}

#################################################
# Lambda Log Group (extract_ingredients lambda) #
#################################################

# Cloudwatch log group for 'extract_ingredients' Python lambda function
resource "aws_cloudwatch_log_group" "extract_ingredients_lambda_log_group" {
  # name_prefix              = "/aws/lambda/${var.extract_ingredients_lambda_function_name}"
  name              = "/aws/lambda/${var.extract_ingredients_lambda_function_name}"
  retention_in_days = 14
  skip_destroy = false
  # skip_destroy = true
}

#########################################################################################################
########### REST API CloudWatch Logs ###########
#########################################################################################################

############################
# FastAPI Lambda Log Group #
############################

# lambda log group
resource "aws_cloudwatch_log_group" "recipe_api_log_group" {
  name              = "/aws/lambda/${var.app_lambda_function_name}"
  # name              = "/aws/lambda/${var.recipes_api_lambda_function_name}"
  retention_in_days = 14
}