# ── ECS Task Execution Role ─────────────────────────────────────────────────
# Allows ECS to pull the image from ECR and write logs to CloudWatch
resource "aws_iam_role" "ecs_execution" {
  name = "${var.project}-ecs-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Execution role needs SSM access to inject secrets before container starts
resource "aws_iam_role_policy" "ecs_execution_ssm" {
  name = "${var.project}-execution-ssm"
  role = aws_iam_role.ecs_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
      Resource = "arn:aws:ssm:${local.region}:${local.account_id}:parameter${var.ssm_prefix}/*"
    }]
  })
}

# ── ECS Task Role ────────────────────────────────────────────────────────────
# What the running container itself is allowed to do
resource "aws_iam_role" "ecs_task" {
  name = "${var.project}-ecs-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Read secrets from SSM Parameter Store (ANTHROPIC_API_KEY, UPLOAD_POST_API_KEY, etc.)
resource "aws_iam_role_policy" "ecs_task_ssm" {
  name = "${var.project}-ssm-read"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
      Resource = "arn:aws:ssm:${local.region}:${local.account_id}:parameter${var.ssm_prefix}/*"
    }]
  })
}

# SNS publish permission — pipeline sends result email after each run
resource "aws_iam_role_policy" "ecs_task_sns" {
  name = "${var.project}-sns-publish"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["sns:Publish"]
      Resource = aws_sns_topic.notify.arn
    }]
  })
}

# S3 access for preview uploads (pre-signed URLs for human review)
resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${var.project}-s3-preview"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject", "s3:GetObject"]
      Resource = "arn:aws:s3:::pencil-shorts-tfstate-339712706640/previews/*"
    }]
  })
}

# ── EventBridge Scheduler Role ───────────────────────────────────────────────
# Allows the scheduler to start ECS tasks
resource "aws_iam_role" "scheduler" {
  name = "${var.project}-scheduler"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_ecs" {
  name = "${var.project}-scheduler-ecs"
  role = aws_iam_role.scheduler.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = [
          aws_ecs_task_definition.short.arn,
          aws_ecs_task_definition.long.arn,
        ]
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = [
          aws_iam_role.ecs_execution.arn,
          aws_iam_role.ecs_task.arn,
        ]
      }
    ]
  })
}
