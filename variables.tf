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

locals {
  project_name        = var.GITHUB_REPO
  account_id          = data.aws_caller_identity.current.account_id
  ecr_repository_name = try(var.AWS_ECR_REPO, "${var.GITHUB_REPO}-${var.ENV_TAG}")
  ecr_image_tag       = "latest"
  lambda_name         = "${var.GITHUB_REPO}-${var.ENV_TAG}"
  bucket_name         = try(var.AWS_BUCKET_NAME, "${var.GITHUB_REPO}-${var.ENV_TAG}")
  env_tag             = var.ENV_TAG
}
