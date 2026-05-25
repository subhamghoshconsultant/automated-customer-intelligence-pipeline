provider "aws" {
  region = "us-east-1"
}

# S3 Bucket for Raw Google Sheets Sync
resource "aws_s3_bucket" "raw_data_bucket" {
  bucket        = "business-intelligence-raw-data-sheets"
  force_destroy = true
}

# S3 Bucket for SageMaker Canvas ML Outputs
resource "aws_s3_bucket" "predictions_bucket" {
  bucket        = "business-intelligence-ml-predictions"
  force_destroy = true
}

output "raw_bucket_arn" {
  value = aws_s3_bucket.raw_data_bucket.arn
}

output "predictions_bucket_arn" {
  value = aws_s3_bucket.predictions_bucket.arn
}
