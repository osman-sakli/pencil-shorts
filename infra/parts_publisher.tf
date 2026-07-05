# ── Bölüm parçası yayın sistemi ──────────────────────────────────────────────
# Lokal üretilen bölüm partları S3 kuyruğuna konur (pipeline/queue_parts.py);
# bu görev her sabah 6 (America/New_York) sıradaki parçayı yayınlar.

resource "aws_s3_bucket" "parts" {
  bucket = "${var.project}-parts-${local.account_id}"
}

resource "aws_s3_bucket_lifecycle_configuration" "parts" {
  bucket = aws_s3_bucket.parts.id
  rule {
    id     = "expire-old-parts"
    status = "Enabled"
    filter { prefix = "parts/" }
    expiration { days = 30 } # yayınlanan partlar 30 gün sonra silinsin
  }
}

resource "aws_iam_role_policy" "ecs_task_parts" {
  name = "${var.project}-parts-queue"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.parts.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.parts.arn
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "publisher" {
  name              = "/ecs/${var.project}-publisher"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "publisher" {
  family                   = "${var.project}-publisher"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name       = "publisher"
    image      = "${local.ecr_url}:latest"
    essential  = true
    entryPoint = ["python3", "publish/publish_queue.py"]
    command    = []

    environment = [
      { name = "QUEUE_BUCKET", value = aws_s3_bucket.parts.bucket },
    ]

    secrets = local.secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.publisher.name
        "awslogs-region"        = local.region
        "awslogs-stream-prefix" = "publish"
      }
    }

    stopTimeout = 120
  }])
}

# Her sabah 06:00 America/New_York (EST/EDT otomatik)
resource "aws_scheduler_schedule" "parts_daily" {
  name       = "${var.project}-parts-daily"
  group_name = "default"

  schedule_expression          = "cron(0 6 * * ? *)"
  schedule_expression_timezone = "America/New_York"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:ecs:${local.region}:${local.account_id}:cluster/${aws_ecs_cluster.main.name}"
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.publisher.arn
      launch_type         = "FARGATE"
      task_count          = 1

      capacity_provider_strategy {
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
      }

      network_configuration {
        assign_public_ip = true
        subnets          = data.aws_subnets.default.ids
        security_groups  = [aws_security_group.ecs_task.id]
      }
    }

    retry_policy {
      maximum_retry_attempts       = 2
      maximum_event_age_in_seconds = 3600
    }
  }
}

# Akşam slotu: 19:00 ET'de highlight yayını (PUBLISH_SLOT=pm override)
resource "aws_scheduler_schedule" "highlights_evening" {
  name       = "${var.project}-highlights-evening"
  group_name = "default"

  schedule_expression          = "cron(0 19 * * ? *)"
  schedule_expression_timezone = "America/New_York"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:ecs:${local.region}:${local.account_id}:cluster/${aws_ecs_cluster.main.name}"
    role_arn = aws_iam_role.scheduler.arn

    input = jsonencode({
      containerOverrides = [{
        name = "publisher"
        environment = [{ name = "PUBLISH_SLOT", value = "pm" }]
      }]
    })

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.publisher.arn
      launch_type         = "FARGATE"
      task_count          = 1

      capacity_provider_strategy {
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
      }

      network_configuration {
        assign_public_ip = true
        subnets          = data.aws_subnets.default.ids
        security_groups  = [aws_security_group.ecs_task.id]
      }
    }

    retry_policy {
      maximum_retry_attempts       = 2
      maximum_event_age_in_seconds = 3600
    }
  }
}
