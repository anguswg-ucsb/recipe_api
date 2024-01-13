################
# API REST API #
################

# Create an API Gateway REST API
resource "aws_api_gateway_rest_api" "recipe_rest_api" {
  name        = var.api_gw_rest_api_name
  description = "Recipes REST API"
}

########################
# API Gateway Resource #
########################

# Create a resource
resource "aws_api_gateway_resource" "recipe_resource" {
  path_part   = "{proxy+}"
  # path_part   = "resource"
  rest_api_id = aws_api_gateway_rest_api.recipe_rest_api.id
  parent_id   = aws_api_gateway_rest_api.recipe_rest_api.root_resource_id
}

#######################################
# API Gateway ANY Method/Integrations #
#######################################

# ANY - METHOD 
# Create an ANY method (proxy integration) for the resource
resource "aws_api_gateway_method" "recipe_api_any_method" {
  rest_api_id   = aws_api_gateway_rest_api.recipe_rest_api.id
  resource_id   = aws_api_gateway_resource.recipe_resource.id
  http_method   = "ANY"
  authorization = "NONE"
}

# ANY - INTEGRATION
# Configure the Lambda function integration for ANY METHOD
resource "aws_api_gateway_integration" "lambda_any_integration" {
  rest_api_id             = aws_api_gateway_rest_api.recipe_rest_api.id
  resource_id             = aws_api_gateway_resource.recipe_resource.id
  http_method             = aws_api_gateway_method.recipe_api_any_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.recipe_api_lambda.invoke_arn
  # uri = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:${var.aws_region}:${var.aws_account_number}:function:${aws_lambda_function.recipe_api_lambda.function_name}/invocations"
  #   request_parameters = {
  #   "method.request.path.proxy" = true
  # }
}

# ANY - METHOD RESPONSE
resource "aws_api_gateway_method_response" "any_200" {
  rest_api_id   = aws_api_gateway_rest_api.recipe_rest_api.id
  resource_id   = aws_api_gateway_resource.recipe_resource.id
  http_method   = "ANY"
  status_code = "200"

  depends_on = [
    aws_api_gateway_integration.lambda_any_integration
  ]
  response_models = {
     "application/json" = "Empty"
  }

}

# ANY - INTEGRATION RESPONSE
resource "aws_api_gateway_integration_response" "any_intergration_response" {

  rest_api_id   = aws_api_gateway_rest_api.recipe_rest_api.id
  resource_id   = aws_api_gateway_resource.recipe_resource.id
  http_method   = "ANY"
  status_code   = aws_api_gateway_method_response.any_200.status_code

   response_templates = {
       "application/json" = ""
   } 
  depends_on = [
    aws_api_gateway_integration.lambda_any_integration
  ]
}

##################################
# API Gateway DEPLOYMENT + STAGE #
##################################

# Create a deployment for the API
resource "aws_api_gateway_deployment" "recipe_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_any_integration
    # aws_api_gateway_integration.lambda_get_integration
    ]

  rest_api_id = aws_api_gateway_rest_api.recipe_rest_api.id
  stage_name  = var.api_gw_stage_name
}

# # Create a stage for the deployment
# resource "aws_api_gateway_stage" "recipe_api_stage" {
#   deployment_id = aws_api_gateway_deployment.recipe_api_deployment.id
#   rest_api_id   = aws_api_gateway_rest_api.recipe_rest_api.id
#   stage_name    = var.api_gw_stage_name

#   # # CloudWatch Logs settings
#   # depends_on = [aws_cloudwatch_log_group.example]
# }

# # method settings for API gateway and allowing cloudwatch logs/metrics
# resource "aws_api_gateway_method_settings" "recipe_api_method_settings" {
#   rest_api_id = aws_api_gateway_rest_api.recipe_rest_api.id
#   stage_name  = aws_api_gateway_stage.recipe_api_stage.stage_name
#   method_path = "*/*"

#   settings {
#     metrics_enabled = true
#     logging_level   = "INFO"
#   }
# }

# ---------------------------------------
# ---- Cloudwatch Logs (API Gateway) ----
# ---------------------------------------

# # Create a CloudWatch Logs group for API Gateway
# resource "aws_cloudwatch_log_group" "recipe_api_gw_logs" {
#   name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.recipe_api_deployment.id}/${var.stage_name}"
#   retention_in_days = 7
# }

###########
# OUTPUTS #
###########

# Output the URL of the API Gateway deployment
output "api_gateway_url" {
  value = aws_api_gateway_deployment.recipe_api_deployment.invoke_url
}

# Output the URL of the API Gateway deployment
output "api_gateway_rest_api_id" {
  value = aws_api_gateway_rest_api.recipe_rest_api.id
}

output "api_gateway_rest_api_execution_arn_custom_ALL" {
  value = "${aws_api_gateway_rest_api.recipe_rest_api.execution_arn}/*/*/*"
}
