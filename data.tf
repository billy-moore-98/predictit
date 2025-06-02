data "aws_ssm_parameter" "s3_bucket" {
  name            = "/lambda/predictit/s3_bucket"
  with_decryption = true
}