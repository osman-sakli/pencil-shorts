variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "pencil-shorts"
}

variable "ecr_repo_name" {
  description = "ECR repository name"
  type        = string
  default     = "pencil-shorts"
}

variable "ssm_prefix" {
  description = "SSM parameter path prefix (no trailing slash)"
  type        = string
  default     = "/pencil-shorts"
}

# Short video schedule: daily at 08:00 AM EDT = 12:00 UTC
variable "short_schedule_expression" {
  description = "EventBridge schedule for daily short videos"
  type        = string
  default     = "cron(0 12 * * ? *)"
}

# Long episode schedule: every 3rd day at 06:00 AM EDT = 10:00 UTC
variable "long_schedule_expression" {
  description = "EventBridge schedule for long episodes"
  type        = string
  default     = "cron(0 10 */3 * ? *)"
}

# ECS short task resources (1 vCPU / 2GB)
variable "short_task_cpu" {
  type    = string
  default = "1024"
}
variable "short_task_memory" {
  type    = string
  default = "2048"
}

# ECS long episode task resources (2 vCPU / 4GB, longer render time)
variable "long_task_cpu" {
  type    = string
  default = "2048"
}
variable "long_task_memory" {
  type    = string
  default = "4096"
}
