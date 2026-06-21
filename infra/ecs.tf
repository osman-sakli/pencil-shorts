# ── ECS Cluster ─────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = var.project

  setting {
    name  = "containerInsights"
    value = "disabled"  # saves ~$5/month; enable if debugging
  }
}

# ── CloudWatch Log Groups ────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "short" {
  name              = "/ecs/${var.project}/short"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "long" {
  name              = "/ecs/${var.project}/long"
  retention_in_days = 14
}

# ── Shared secret references from SSM ───────────────────────────────────────
locals {
  secrets = [
    { name = "ANTHROPIC_API_KEY",    valueFrom = "${var.ssm_prefix}/anthropic_api_key" },
    { name = "UPLOAD_POST_API_KEY",  valueFrom = "${var.ssm_prefix}/upload_post_api_key" },
    { name = "UPLOAD_POST_USER",     valueFrom = "${var.ssm_prefix}/UPLOAD_POST_USER" },
    { name = "AFFILIATE_LINK",       valueFrom = "${var.ssm_prefix}/affiliate_link" },
  ]
}

# ── Short Video Task Definition (daily, 1 vCPU / 2 GB) ─────────────────────
resource "aws_ecs_task_definition" "short" {
  family                   = "${var.project}-short"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.short_task_cpu
  memory                   = var.short_task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "pipeline"
    image     = "${local.ecr_url}:latest"
    essential = true

    # Run: python3 pipeline/run.py --auto
    command = ["--auto"]

    environment = [
      { name = "TTS_PROVIDER", value = "edge" },
      { name = "LLM_MODEL",    value = "claude-haiku-4-5-20251001" },
    ]

    secrets = local.secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.short.name
        "awslogs-region"        = local.region
        "awslogs-stream-prefix" = "run"
      }
    }

    stopTimeout = 120
  }])
}

# ── Long Episode Task Definition (every 3 days, 2 vCPU / 4 GB) ─────────────
resource "aws_ecs_task_definition" "long" {
  family                   = "${var.project}-long"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.long_task_cpu
  memory                   = var.long_task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "pipeline"
    image     = "${local.ecr_url}:latest"
    essential = true

    # Unified long episode — single coherent story, single render
    entryPoint = ["python3", "pipeline/run_long_unified.py"]
    command    = ["--auto"]

    environment = [
      { name = "TTS_PROVIDER", value = "edge" },
      { name = "LLM_MODEL",    value = "claude-haiku-4-5-20251001" },
    ]

    secrets = local.secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.long.name
        "awslogs-region"        = local.region
        "awslogs-stream-prefix" = "episode"
      }
    }

    stopTimeout = 120  # Fargate max is 120s
  }])
}

# ── Long Episode Preview Task (render only, uploads to S3 for review) ───────
resource "aws_ecs_task_definition" "long_preview" {
  family                   = "${var.project}-long-preview"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.long_task_cpu
  memory                   = var.long_task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "pipeline"
    image     = "${local.ecr_url}:latest"
    essential = true

    entryPoint = ["python3", "pipeline/run_long_unified.py"]
    command    = ["--auto", "--no-publish"]

    environment = [
      { name = "TTS_PROVIDER", value = "edge" },
      { name = "LLM_MODEL",    value = "claude-haiku-4-5-20251001" },
    ]

    secrets = local.secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.long.name
        "awslogs-region"        = local.region
        "awslogs-stream-prefix" = "preview"
      }
    }

    stopTimeout = 120
  }])
}

output "short_task_definition_arn" {
  value = aws_ecs_task_definition.short.arn
}

output "long_task_definition_arn" {
  value = aws_ecs_task_definition.long.arn
}
