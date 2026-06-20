# Use default VPC and subnets — cheapest option, no NAT gateway needed
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security group: outbound only (needs internet for EdgeTTS, upload-post, Anthropic)
resource "aws_security_group" "ecs_task" {
  name        = "${var.project}-ecs-task"
  description = "Allow outbound for pipeline tasks"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
