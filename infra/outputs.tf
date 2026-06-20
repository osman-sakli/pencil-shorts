output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecr_url" {
  value = local.ecr_url
}

output "run_short_now_cmd" {
  description = "Run a short video task immediately (one-shot test)"
  value = <<-EOT
    aws ecs run-task \
      --cluster ${aws_ecs_cluster.main.name} \
      --task-definition ${aws_ecs_task_definition.short.family} \
      --launch-type FARGATE \
      --network-configuration "awsvpcConfiguration={subnets=[${join(",", data.aws_subnets.default.ids)}],securityGroups=[${aws_security_group.ecs_task.id}],assignPublicIp=ENABLED}" \
      --region ${local.region}
  EOT
}

output "run_long_now_cmd" {
  description = "Run a long episode task immediately (one-shot test)"
  value = <<-EOT
    aws ecs run-task \
      --cluster ${aws_ecs_cluster.main.name} \
      --task-definition ${aws_ecs_task_definition.long.family} \
      --launch-type FARGATE \
      --network-configuration "awsvpcConfiguration={subnets=[${join(",", data.aws_subnets.default.ids)}],securityGroups=[${aws_security_group.ecs_task.id}],assignPublicIp=ENABLED}" \
      --region ${local.region}
  EOT
}

output "logs_short_cmd" {
  description = "Tail short video logs"
  value = "aws logs tail /ecs/${var.project}/short --follow --region ${local.region}"
}

output "logs_long_cmd" {
  description = "Tail long episode logs"
  value = "aws logs tail /ecs/${var.project}/long --follow --region ${local.region}"
}
