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

module "iam" {
  source = "./infrastructure/aws/iam"
  lambda_ex_role_name = "lambda_ex"
}

module "s3_bucket" {
  source = "./infrastructure/aws/s3"
  s3_bucket_name = var.s3_bucket_name
}

module "lambdas" {
  source = "./infrastructure/aws/lambdas"
  lambda_ex_role_arn = module.iam.lambda_ex_role_arn
  s3_bucket_name = module.s3_bucket.s3_bucket_name
}