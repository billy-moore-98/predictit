terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
  region = "eu-west-2"
}

resource "aws_s3_bucket" "predictit_bucket" {
  bucket = data.aws_ssm_parameter.s3_bucket.value

  tags = {
    project = "predictit"
  }
}

module "iam" {
  source = "./infrastructure/aws/iam"
  lambda_ex_role_name = "lambda_ex"
}

resource "aws_lambda_function" "lambda_fetch" {
  function_name = "predictit-fetch"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.predictit_fetch.repository_url}:latest"
  role          = module.iam.lambda_ex_role_arn
  timeout       = 3
  memory_size   = 128
  architectures = ["x86_64"]

  environment {
    variables = {
        S3_BUCKET = data.aws_ssm_parameter.s3_bucket.value
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
  role          = module.iam.lambda_ex_role_arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.predictit_validate.repository_url}:latest"
  memory_size   = 128
  timeout       = 3
  architectures = ["x86_64"]
  reserved_concurrent_executions = -1

  environment {
    variables = {
        S3_BUCKET = data.aws_ssm_parameter.s3_bucket.value
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