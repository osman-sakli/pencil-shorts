# GitHub Actions → AWS OIDC (password-free auth, no long-lived keys)
# Replace YOUR_GITHUB_ORG/YOUR_REPO with actual values (e.g. osmansakli/pencil-shorts)

variable "github_repo" {
  description = "GitHub repo in org/repo format"
  type        = string
  default     = "osman-sakli/pencil-shorts"
}

data "aws_iam_openid_connect_provider" "github" {
  # If OIDC provider doesn't exist yet, uncomment the resource block below
  # and comment out this data block
  url = "https://token.actions.githubusercontent.com"
}

# Uncomment this if the OIDC provider doesn't exist in your account:
# resource "aws_iam_openid_connect_provider" "github" {
#   url             = "https://token.actions.githubusercontent.com"
#   client_id_list  = ["sts.amazonaws.com"]
#   thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
# }

resource "aws_iam_role" "github_actions_deploy" {
  name = "${var.project}-github-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = data.aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "github_deploy_permissions" {
  name = "${var.project}-github-deploy-perms"
  role = aws_iam_role.github_actions_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR: push images
      {
        Effect   = "Allow"
        Action   = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
        ]
        Resource = "*"
      },
      # S3: terraform state
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::pencil-shorts-tfstate-339712706640",
          "arn:aws:s3:::pencil-shorts-tfstate-339712706640/*",
        ]
      },
      # ECS + IAM PassRole for Terraform apply
      {
        Effect   = "Allow"
        Action   = [
          "ecs:*",
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:PassRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:CreateOpenIDConnectProvider",
          "iam:GetOpenIDConnectProvider",
        ]
        Resource = "*"
      },
      # EventBridge Scheduler
      {
        Effect   = "Allow"
        Action   = ["scheduler:*"]
        Resource = "*"
      },
      # CloudWatch Logs
      {
        Effect   = "Allow"
        Action   = ["logs:*"]
        Resource = "*"
      },
      # Budgets
      {
        Effect   = "Allow"
        Action   = ["budgets:*"]
        Resource = "*"
      },
      # EC2 for VPC/SG reads and security group management
      {
        Effect   = "Allow"
        Action   = [
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:CreateSecurityGroup",
          "ec2:DeleteSecurityGroup",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:CreateTags",
        ]
        Resource = "*"
      },
    ]
  })
}

output "github_actions_role_arn" {
  description = "Add this as AWS_DEPLOY_ROLE_ARN in GitHub repo secrets"
  value       = aws_iam_role.github_actions_deploy.arn
}
