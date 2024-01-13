######################
# EC2 Security group #
######################

# Security group for the EC2 instance
resource "aws_security_group" "ec2_sg" {
  name        = "ec2_sg"
  description = "Security group for the EC2 Postgres DB instance"
  vpc_id      = data.aws_vpc.main_vpc.id

  # Rule to allow SSH (port 22) access from specified IP addresses
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.env_ip}/32"]
  }

  # Rule to allow PostgreSQL (port 5432) access from specified IP addresses
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${var.env_ip}/32"]
  }

  # Rule to allow SSH (port 22) access from specified IP addresses
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ip_addresses
  }
  # Rule to allow PostgreSQL (port 5432) access from your personal IP
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_ip_addresses
  }

  # # Rule to allow traffic from the Lambda security group
  ingress {
    from_port         = 5432
    to_port           = 5432
    protocol          = "tcp"
    # security_groups   = [data.aws_security_group.lambda_sg.id]
    security_groups   = [aws_security_group.lambda_sg.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ec2_sg"
  }

  depends_on = [
    # aws_instance.ec2_db_instance,
    aws_security_group.lambda_sg
  ]
}

#########################
# Lambda Security group #
#########################

resource "aws_security_group" "lambda_sg" {
    name = var.lambda_sg_name
    vpc_id      = data.aws_vpc.main_vpc.id

    # ingress {
    #     from_port = 80
    #     to_port = 80
    #     protocol = "tcp"
    #     cidr_blocks = ["0.0.0.0/0"]
    # }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

  lifecycle {
    create_before_destroy = true
  }

}