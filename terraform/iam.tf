resource "aws_iam_role" "mlflowrole" {
  name = "mlflowrole"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach_s3_access" {
  role       = aws_iam_role.mlflowrole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "attach_rds_access" {
  role       = aws_iam_role.mlflowrole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_instance_profile" "profile" {
  name = "mlflowfroge"
  role = aws_iam_role.mlflowrole.name
}