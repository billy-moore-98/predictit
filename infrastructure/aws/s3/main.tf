resource "aws_s3_bucket" "predictit_bucket" {
    bucket = var.s3_bucket_name

    tags = {
        project = "predictit"
    }
}