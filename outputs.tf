output "lambda_function" {
  value = aws_lambda_function.lambda.id
}

output "bucket_name" {
  value = aws_s3_bucket.bucket.id
}

output "ecr_repo" {
  value = local.ecr_repository_name
}
