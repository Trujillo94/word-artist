# Create an API Gateway REST API
resource "aws_api_gateway_rest_api" "api" {
  name        = "${local.project_name}-api"
  description = "WordArtist REST API."
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "slack"
}

resource "aws_api_gateway_method" "lambda" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.lambda.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.lambda.id
  http_method = aws_api_gateway_method.lambda.http_method

  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.lambda.invoke_arn
  timeout_milliseconds    = 29000

  request_parameters = {
    "integration.request.header.X-Authorization" = "'static'"
  }

  request_templates = {
    "application/json"                  = "$input.json('$.body')"
    "application/x-www-form-urlencoded" = <<EOF
## Parses x-www-urlencoded data to JSON for AWS' API Gateway
##
## Author: Oriol Trujillo <trujillo.oriol@gmail.io>

#if ( $context.httpMethod == "POST" )
  #set( $requestBody = $input.path('$') )
#else
  #set( $requestBody = "" )
#end

#set( $keyValuePairs = $requestBody.split("&") )
#set( $params = [] )

## Filter empty key-value pairs
#foreach( $kvp in $keyValuePairs )
  #set( $operands = $kvp.split("=") )

  #if( $operands.size() == 1 || $operands.size() == 2 )
    #set( $success = $params.add($operands) )
  #end
#end

{
  #foreach( $param in $params )
    #set( $key = $util.urlDecode($param[0]) )

    #if( $param.size() > 1 )
      #set( $value = $util.urlDecode($param[1]) )
    #else
      #set( $value = "" )
    #end
    #if( $value.toString().contains("{") || $value.toString().contains("{") )
        "$key": $value#if( $foreach.hasNext ),#end
    #else
        "$key": "$value"#if( $foreach.hasNext ),#end
    #end
  #end
}
    EOF
  }
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.lambda.id
  http_method = aws_api_gateway_method.lambda.http_method
  status_code = "200"
  # response_models = "application/json => Empty"
}

resource "aws_api_gateway_integration_response" "integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.lambda.id
  http_method = aws_api_gateway_method.lambda.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code
}

resource "aws_api_gateway_method" "method_root" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_rest_api.api.root_resource_id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_method.method_root.resource_id
  http_method = aws_api_gateway_method.method_root.http_method

  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  # stage_name  = local.env_tag
  variables = {
    deployed_at = var.deployed_at
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api-stage" {
  deployment_id = aws_api_gateway_deployment.apideploy.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  # stage_name    = aws_api_gateway_deployment.apideploy.stage_name
  stage_name = local.env_tag
}

resource "aws_api_gateway_method_settings" "api-settings" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.api-stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

output "base_url" {
  value = aws_api_gateway_deployment.apideploy.invoke_url
}

