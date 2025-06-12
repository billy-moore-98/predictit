resource "aws_lambda_function" "lambda_fetch" {
  function_name = "predictit-fetch"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.predictit_fetch.repository_url}:latest"
  role          = var.lambda_ex_role_arn
  timeout       = 3
  memory_size   = 128
  architectures = ["x86_64"]

  environment {
    variables = {
        S3_BUCKET = var.s3_bucket_name
    }
  }

  ephemeral_storage {
    size = 512
  }

  logging_config {
    log_format = "Text"
    log_group = "/aws/lambda/predictit-fetch"
  }

  tracing_config {
    mode = "PassThrough"
  }

  tags = {
    project = "predictit"
  }
}

resource "aws_lambda_function" "lambda_validate" {
  function_name = "predictit-validate"
  role          = var.lambda_ex_role_arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.predictit_validate.repository_url}:latest"
  memory_size   = 128
  timeout       = 3
  architectures = ["x86_64"]
  reserved_concurrent_executions = -1

  environment {
    variables = {
        S3_BUCKET = var.s3_bucket_name
    }
  }

  ephemeral_storage {
    size = 512
  }

  logging_config {
    log_format = "Text"
    log_group = "/aws/lambda/predictit-validate"
  }

  tracing_config {
    mode = "PassThrough"
  }

  tags = {
    project = "predictit"
  }
}

resource "aws_ecr_repository" "predictit_fetch" {
  name                 = "predictit-fetch"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    project = "predictit"
  }
}

resource "aws_ecr_repository" "predictit_validate" {
  name                 = "predictit-validate"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    project = "predictit"
  }
}