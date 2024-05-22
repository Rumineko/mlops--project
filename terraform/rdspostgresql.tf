resource "aws_security_group" "mlflow_db_sg" {
  name        = "mlflow_db_sg"
  description = "Allow inbound traffic to mlflow_db"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  // Replace this with your IP range
  }

  tags = {
    Name = "mlflow_db_sg"
  }
}

resource "aws_db_instance" "mlflow_db" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "16.3"
  instance_class       = "db.t3.micro"
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres16"
  skip_final_snapshot  = true
  publicly_accessible  = true
  multi_az             = false
  identifier           = "mlflowfroge"
  vpc_security_group_ids = [aws_security_group.mlflow_db_sg.id]

  tags = {
    Name = "MLFlow-DB"
  }
}