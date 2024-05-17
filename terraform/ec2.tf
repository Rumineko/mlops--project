resource "aws_instance" "mlflow" {
  ami             = "ami-0233214e13e500f77" # Replace with a valid AMI ID for eu-central-1
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.mykey.key_name
  security_groups = [aws_security_group.mlflow_sg.name]

  tags = {
    Name = "MLFlow-Instance"
  }
  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo amazon-linux-extras install docker -y
              sudo service docker start
              sudo usermod -a -G docker ec2-user

              # Install pip and MLflow
              sudo yum install python3 -y
              pip3 install mlflow boto3 psycopg2-binary

              # Run MLflow server
              mlflow server \
                --backend-store-uri postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.mlflow_db.address}:5432/mlflowdb \
                --default-artifact-root s3://${aws_s3_bucket.mlflow_bucket.bucket} \
                --host 0.0.0.0 --port 8080
              EOF
}

output "instance_public_ip" {
  value = aws_instance.mlflow.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.mlflow_db.endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.mlflow_bucket.bucket
}