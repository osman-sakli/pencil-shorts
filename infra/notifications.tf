# ── SNS Email Notifications ──────────────────────────────────────────────────
resource "aws_sns_topic" "notify" {
  name = "${var.project}-notify"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.notify.arn
  protocol  = "email"
  endpoint  = "osmansakli@yahoo.com"
}

output "sns_topic_arn" {
  value       = aws_sns_topic.notify.arn
  description = "SNS topic ARN for pipeline notifications"
}
