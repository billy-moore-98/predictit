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
}

resource "aws_lambda_function" "lambda_fetch" {
  function_name = "predictit-fetch"
  package_type  = "Image"
  image_uri     = "299579973471.dkr.ecr.eu-west-2.amazonaws.com/predictit-fetch:latest"
  role          = "arn:aws:iam::299579973471:role/lambda-ex"
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
}

resource "aws_lambda_function" "lambda_validate" {
  function_name = "predictit-validate"
  role          = "arn:aws:iam::299579973471:role/lambda-ex"
  package_type  = "Image"
  image_uri     = "299579973471.dkr.ecr.eu-west-2.amazonaws.com/predictit-validate:latest"
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
}