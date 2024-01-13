# # ##############################
# # # SECRETS MANAGERS RDS PROXY #
# # ##############################

resource "aws_secretsmanager_secret" "ec2_db_secret" {
  name_prefix = var.ec2_secret_prefix
  recovery_window_in_days = 0
  description = "Secret for EC2 DB instance"
}

# # aws_rds_cluster.aurora_dish_recipes_cluster.iam_database_authentication_enabled
# # aws_rds_cluster_instance.aurora_dish_recipes_instance
resource "aws_secretsmanager_secret_version" "ec2_secret_version" {
  secret_id     = aws_secretsmanager_secret.ec2_db_secret.id
  secret_string = jsonencode({
    "username"             = var.db_username
    "password"             = var.db_password
    "db_name"              = var.db_name
    "engine"               = "postgres"
    "port"                 = var.db_port_int
  })
}