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

variable "AWS_LAMBDA_FUNCTION" {
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
  ecr_repository_name = try(var.AWS_ECR_REPO, "${var.GITHUB_REPO}-${var.ENV_TAG}")
  ecr_image_tag       = "latest"
  lambda_name         = try(var.AWS_LAMBDA_FUNCTION, "${var.GITHUB_REPO}-${var.ENV_TAG}")
  bucket_name         = try(var.AWS_BUCKET_NAME, "${var.GITHUB_REPO}-${var.ENV_TAG}")
  env_tag             = var.ENV_TAG
}

# Create a new ECR repository
resource "aws_ecr_repository" "repo" {
  name = local.ecr_repository_name
}

resource "null_resource" "ecr_image" {
  # triggers = {
  #   python_file = md5(file("${path.module}/main.py"))
  #   docker_file = md5(file("${path.module}/Dockerfile"))
  # }

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
  name               = "${local.lambda_name}-lambda-role"
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

  # statement {
  #   actions = [
  #     "s3:GetObject",
  #     "s3:PutObject"
  #   ]
  #   effect    = "Allow"
  #   resources = ["*"]
  #   sid       = "S3"
  # }
}

resource "aws_iam_policy" "lambda" {
  name = "${local.lambda_name}-lambda-policy"
  path = "/"
  # policy = data.aws_iam_policy_document.lambda.json
  policy = <<-EOF
          {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": ["arn:aws:s3:::{var.bucket_name}"]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": ["arn:aws:s3:::{var.bucket_name}/*"]
                }
            ]
          }
        EOF
}

resource "aws_iam_role_policy_attachment" "lambda-role-policy-attachment" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda.arn
}

resource "aws_lambda_function" "lambda" {
  depends_on = [
    null_resource.ecr_image
  ]
  function_name = local.lambda_name
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
resource "aws_api_gateway_rest_api" "api" {
  name        = "${local.project_name}-api"
  description = "WordArtist REST API."
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "slack"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = aws_api_gateway_method.method.http_method

  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.lambda.invoke_arn
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
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = aws_api_gateway_method.method.http_method
  status_code = "200"
  # response_models = "application/json => Empty"
}

resource "aws_api_gateway_integration_response" "api_gateway_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = aws_api_gateway_method.method.http_method
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
    aws_api_gateway_integration.integration,
    aws_api_gateway_integration.lambda_root
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = local.env_tag
  variables = {
    deployed_at = var.deployed_at
  }
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}


# Create an S3 bucket
resource "aws_s3_bucket" "bucket" {
  bucket = local.bucket_name
  versioning {
    enabled = false
  }
}

resource "aws_s3_access_point" "bucket_lambda_access_point" {
  bucket = aws_s3_bucket.bucket.id
  name   = "${var.AWS_BUCKET_NAME}-lambda"
}

# resource "aws_s3control_access_point_policy" "example" {
#   access_point_arn = aws_s3_access_point.bucket_lambda_access_point.arn

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect = "Allow"
#       Action = [
#         "s3:GetObject"
#       ],
#       Sid = "s3-object-lambda",
#       Principal = {
#         AWS = "*"
#       }
#       Resource = "${aws_s3_access_point.bucket_lambda_access_point.arn}/object/*"
#       # Resource = ["*"]
#     }]
#   })
# }

# resource "aws_s3control_object_lambda_access_point" "bucket_lambda_access_point_control_object" {
#   name = "${var.AWS_BUCKET_NAME}-lambda"

#   configuration {
#     supporting_access_point = aws_s3_access_point.bucket_lambda_access_point.arn

#     transformation_configuration {
#       actions = ["PutObject"]

#       content_transformation {
#         aws_lambda {
#           function_arn = aws_lambda_function.lambda.arn
#         }
#       }
#     }
#   }
# }

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.bucket.id
  acl    = "private"
}

output "lambda_function" {
  value = aws_lambda_function.lambda.id
}

output "base_url" {
  value = aws_api_gateway_deployment.apideploy.invoke_url
}

output "bucket_name" {
  value = aws_s3_bucket.bucket.id
}

output "ecr_repo" {
  value = aws_ecr_repository.repo.id
}

