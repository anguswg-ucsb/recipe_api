####################
# VPC and Subnet IDs
####################

data "aws_vpc" "main_vpc" {
  id = var.vpc_id
  # id = "vpc-06a9576a46a4e4979"
}

# Default VPC subnet 1 data block
data "aws_subnet" "default_subnet1" {
  id = var.subnet_id1
}

# Default VPC subnet 1 data block
data "aws_subnet" "default_subnet2" {
  id = var.subnet_id2
}