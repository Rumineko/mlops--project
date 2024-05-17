resource "aws_s3_bucket" "mlflow_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "MLFlow-Artifacts-Bucket"
  }
}