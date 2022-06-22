terraform {

  cloud {
    organization = "oriol-trujillo"
    workspaces {
      name = "word-artist"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

variable "AWS_ACCESS_KEY_ID" {
  type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
}

variable "AWS_REGION" {
  type = string
}

variable "AWS_BUCKET_NAME" {
  type      = string
  sensitive = false
  nullable  = false
}

variable "GITHUB_REPO" {
  type      = string
  sensitive = false
  nullable  = false
}

variable "AWS_ECR_REPO" {
  type      = string
  sensitive = false
  nullable  = true
}

variable "ENV_TAG" {
  type      = string
  sensitive = false
  nullable  = true
}

variable "deployed_at" {
  type      = string
  sensitive = false
  nullable  = false
}

provider "aws" {
  region     = var.AWS_REGION
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
}

data "aws_caller_identity" "current" {}

locals {
  project_name        = var.GITHUB_REPO
  account_id          = data.aws_caller_identity.current.account_id
  ecr_repository_name = try(var.AWS_ECR_REPO, local.project_name)
  ecr_image_tag       = "latest"
  env_tag             = var.ENV_TAG
}

# Create a new ECR repository
resource "aws_ecr_repository" "repo" {
  name = local.ecr_repository_name
}

resource "null_resource" "ecr_image" {
  triggers = {
    python_file = md5(file("${path.module}/main.py"))
    docker_file = md5(file("${path.module}/Dockerfile"))
  }

  provisioner "local-exec" {
    command = <<EOF
           aws ecr get-login-password --region ${var.AWS_REGION} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.AWS_REGION}.amazonaws.com
           cd ${path.module}/
           docker build -t ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag} .
           docker push ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag}
       EOF
  }
}

data "aws_ecr_image" "lambda_image" {
  depends_on = [
    null_resource.ecr_image
  ]
  repository_name = local.ecr_repository_name
  image_tag       = local.ecr_image_tag
}

# Create a new Lambda function
resource "aws_iam_role" "lambda" {
  name               = "${local.project_name}-lambda-role"
  assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Action": "sts:AssumeRole",
           "Principal": {
               "Service": "lambda.amazonaws.com"
           },
           "Effect": "Allow"
       }
   ]
}
 EOF
}

data "aws_iam_policy_document" "lambda" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect    = "Allow"
    resources = ["*"]
    sid       = "CreateCloudWatchLogs"
  }

  statement {
    actions = [
      "codecommit:GitPull",
      "codecommit:GitPush",
      "codecommit:GitBranch",
      "codecommit:ListBranches",
      "codecommit:CreateCommit",
      "codecommit:GetCommit",
      "codecommit:GetCommitHistory",
      "codecommit:GetDifferences",
      "codecommit:GetReferences",
      "codecommit:BatchGetCommits",
      "codecommit:GetTree",
      "codecommit:GetObjectIdentifier",
      "codecommit:GetMergeCommit"
    ]
    effect    = "Allow"
    resources = ["*"]
    sid       = "CodeCommit"
  }
}

resource "aws_iam_policy" "lambda" {
  name   = "${local.project_name}-lambda-policy"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda.json
}

resource "aws_lambda_function" "sample_lambda" {
  depends_on = [
    null_resource.ecr_image
  ]
  function_name = "${local.project_name}-${local.env_tag}"
  role          = aws_iam_role.lambda.arn
  timeout       = 30
  image_uri     = "${aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
  environment {
    variables = {
      AWS_BUCKET_NAME = var.AWS_BUCKET_NAME
    }
  }
}

# Create an API Gateway REST API
resource "aws_api_gateway_rest_api" "sample_api" {
  name        = "${local.project_name}-api"
  description = "WordArtist REST API."
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "sample_resource" {
  rest_api_id = aws_api_gateway_rest_api.sample_api.id
  parent_id   = aws_api_gateway_rest_api.sample_api.root_resource_id
  path_part   = "slack"
}

resource "aws_api_gateway_method" "sample_method" {
  rest_api_id   = aws_api_gateway_rest_api.sample_api.id
  resource_id   = aws_api_gateway_resource.sample_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "sample_integration" {
  rest_api_id = aws_api_gateway_rest_api.sample_api.id
  resource_id = aws_api_gateway_resource.sample_resource.id
  http_method = aws_api_gateway_method.sample_method.http_method

  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.sample_lambda.invoke_arn
  timeout_milliseconds    = 29000

  request_parameters = {
    "integration.request.header.X-Authorization" = "'static'"
  }

  # Transforms the incoming XML request to JSON
  request_templates = {
    "application/xml" = <<EOF
    {
      "body" : $input.json('$')
    }
    EOF
  }
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.sample_api.id
  resource_id = aws_api_gateway_resource.sample_resource.id
  http_method = aws_api_gateway_method.sample_method.http_method
  status_code = "200"
  # response_models = "application/json => Empty"
}

resource "aws_api_gateway_integration_response" "MyDemoIntegrationResponse" {
  rest_api_id = aws_api_gateway_rest_api.sample_api.id
  resource_id = aws_api_gateway_resource.sample_resource.id
  http_method = aws_api_gateway_method.sample_method.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code
}

resource "aws_api_gateway_method" "method_root" {
  rest_api_id   = aws_api_gateway_rest_api.sample_api.id
  resource_id   = aws_api_gateway_rest_api.sample_api.root_resource_id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.sample_api.id
  resource_id = aws_api_gateway_method.method_root.resource_id
  http_method = aws_api_gateway_method.method_root.http_method

  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.sample_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.sample_integration,
    aws_api_gateway_integration.lambda_root
  ]

  rest_api_id = aws_api_gateway_rest_api.sample_api.id
  stage_name  = local.env_tag
  variables = {
    deployed_at = var.deployed_at
  }
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sample_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "${aws_api_gateway_rest_api.sample_api.execution_arn}/*/*"
}


# Create an S3 bucket
resource "aws_s3_bucket" "bucket" {
  bucket = try(var.AWS_BUCKET_NAME, local.project_name)
  versioning {
    enabled = false
  }
}

resource "aws_s3_access_point" "sample_lambda_access_point" {
  bucket = aws_s3_bucket.bucket.id
  name   = "sample_bucket"
}

resource "aws_s3control_object_lambda_access_point" "sample_lambda_access_point" {
  name = "sample_lambda_access_point"

  configuration {
    supporting_access_point = aws_s3_access_point.sample_lambda_access_point.arn

    transformation_configuration {
      actions = ["GetObject", "PutObject"]

      content_transformation {
        aws_lambda {
          function_arn = aws_lambda_function.sample_lambda.arn
        }
      }
    }
  }
}

resource "aws_s3_bucket_acl" "sample_bucket_acl" {
  bucket = aws_s3_bucket.bucket.id
  acl    = "private"
}

output "lambda_name" {
  value = aws_lambda_function.sample_lambda.id
}

output "base_url" {
  value = aws_api_gateway_deployment.apideploy.invoke_url
}

output "bucket_name" {
  value = aws_s3_bucket.bucket.id
}

