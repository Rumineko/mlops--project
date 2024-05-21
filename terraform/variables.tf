variable "aws_region" {
  default = "eu-central-1"
}

variable "db_username" {
  description = "The username for the RDS instance"
  default     = "wakemeupinside"
}

variable "db_password" {
  description = "The password for the RDS instance"
  default     = "icantwakeup"
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for MLflow artifacts"
  default     = "mlflowfroge"
}