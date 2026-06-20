# ── EventBridge Scheduler: Short Video (daily 14:00 UTC) ────────────────────
resource "aws_scheduler_schedule" "short_daily" {
  name       = "${var.project}-short-daily"
  group_name = "default"

  schedule_expression          = var.short_schedule_expression  # cron(0 14 * * ? *)
  schedule_expression_timezone = "UTC"

  flexible_time_window {
    mode = "OFF"  # exact time, no drift
  }

  target {
    arn      = "arn:aws:ecs:${local.region}:${local.account_id}:cluster/${aws_ecs_cluster.main.name}"
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.short.arn
      launch_type         = "FARGATE"
      task_count          = 1

      # Spot = ~70% cheaper, ok for non-critical daily render
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
      maximum_event_age_in_seconds = 3600  # give up after 1h
    }
  }
}

# ── EventBridge Scheduler: Long Episode (every 3 days 08:00 UTC) ────────────
resource "aws_scheduler_schedule" "long_episode" {
  name       = "${var.project}-long-episode"
  group_name = "default"

  schedule_expression          = var.long_schedule_expression  # rate(3 days)
  schedule_expression_timezone = "UTC"

  flexible_time_window {
    # Allow up to 10-minute drift to avoid thundering-herd with short task
    mode                      = "FLEXIBLE"
    maximum_window_in_minutes = 10
  }

  target {
    arn      = "arn:aws:ecs:${local.region}:${local.account_id}:cluster/${aws_ecs_cluster.main.name}"
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.long.arn
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
      maximum_retry_attempts       = 1   # long episodes are expensive, fail fast
      maximum_event_age_in_seconds = 7200
    }
  }
}

# ── Kill switch outputs ──────────────────────────────────────────────────────
output "disable_short_schedule_cmd" {
  value = "aws scheduler update-schedule --name ${aws_scheduler_schedule.short_daily.name} --state DISABLED --schedule-expression '${var.short_schedule_expression}' --flexible-time-window '{\"Mode\":\"OFF\"}' --target '{\"Arn\":\"arn:aws:ecs:${local.region}:${local.account_id}:cluster/${aws_ecs_cluster.main.name}\",\"RoleArn\":\"${aws_iam_role.scheduler.arn}\"}'"
  description = "Command to pause the daily short schedule"
}

output "disable_long_schedule_cmd" {
  value = "aws scheduler update-schedule --name ${aws_scheduler_schedule.long_episode.name} --state DISABLED --schedule-expression '${var.long_schedule_expression}' --flexible-time-window '{\"Mode\":\"OFF\"}' --target '{\"Arn\":\"arn:aws:ecs:${local.region}:${local.account_id}:cluster/${aws_ecs_cluster.main.name}\",\"RoleArn\":\"${aws_iam_role.scheduler.arn}\"}'"
  description = "Command to pause the long episode schedule"
}
