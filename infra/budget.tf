# Cost alarm — alert if monthly AWS spend exceeds $10
# Sır değerleri ASLA repoya yazma — e-posta adresi değişken olarak SSM'den gelir
variable "budget_alert_email" {
  description = "Email to receive budget alerts (do not commit the value)"
  type        = string
  default     = ""  # Set via: terraform apply -var='budget_alert_email=you@example.com'
}

resource "aws_budgets_budget" "monthly" {
  count = var.budget_alert_email != "" ? 1 : 0

  name         = "${var.project}-monthly"
  budget_type  = "COST"
  limit_amount = "10"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.budget_alert_email]
  }
}
