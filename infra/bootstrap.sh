#!/bin/bash
# infra/bootstrap.sh — One-time setup before first terraform apply
# Run this ONCE manually. After this, everything is automated.
# Sır değerleri ASLA repoya yazma — sadece SSM'e

set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
PREFIX="/pencil-shorts"

echo "=== Pencil Shorts Bootstrap ==="
echo "Region: $REGION"
echo ""

# ── 1. Check AWS auth ────────────────────────────────────────────────────────
echo "[1/5] AWS kimlik doğrulama kontrol..."
aws sts get-caller-identity --region "$REGION" || {
  echo "ERROR: AWS oturumu açık değil. 'aws configure' veya 'aws sso login' çalıştır."
  exit 1
}

# ── 2. SSM secrets ──────────────────────────────────────────────────────────
echo ""
echo "[2/5] SSM secret'ları yükleniyor..."
echo "Her değeri girmek için Enter'a bas. Boş bırakırsan o secret atlanır."
echo ""

read -rsp "ANTHROPIC_API_KEY (sk-ant-...): " ANTHROPIC_KEY
echo ""
if [ -n "$ANTHROPIC_KEY" ]; then
  aws ssm put-parameter \
    --name "$PREFIX/ANTHROPIC_API_KEY" \
    --value "$ANTHROPIC_KEY" \
    --type SecureString \
    --overwrite \
    --region "$REGION"
  echo "  ✅ ANTHROPIC_API_KEY kaydedildi"
fi

read -rsp "UPLOAD_POST_API_KEY: " UPLOADPOST_KEY
echo ""
if [ -n "$UPLOADPOST_KEY" ]; then
  aws ssm put-parameter \
    --name "$PREFIX/UPLOAD_POST_API_KEY" \
    --value "$UPLOADPOST_KEY" \
    --type SecureString \
    --overwrite \
    --region "$REGION"
  echo "  ✅ UPLOAD_POST_API_KEY kaydedildi"
fi

read -rsp "UPLOAD_POST_USER (örn. familypencils): " UPLOADPOST_USER
echo ""
if [ -n "$UPLOADPOST_USER" ]; then
  aws ssm put-parameter \
    --name "$PREFIX/UPLOAD_POST_USER" \
    --value "$UPLOADPOST_USER" \
    --type String \
    --overwrite \
    --region "$REGION"
  echo "  ✅ UPLOAD_POST_USER kaydedildi"
fi

read -rsp "AFFILIATE_LINK (boş bırakılabilir): " AFFILIATE
echo ""
if [ -n "$AFFILIATE" ]; then
  aws ssm put-parameter \
    --name "$PREFIX/AFFILIATE_LINK" \
    --value "$AFFILIATE" \
    --type String \
    --overwrite \
    --region "$REGION"
  echo "  ✅ AFFILIATE_LINK kaydedildi"
fi

# ── 3. ECR repo (Terraform öncesi gerekli) ──────────────────────────────────
echo ""
echo "[3/5] ECR repository oluşturuluyor (zaten varsa atlanır)..."
aws ecr describe-repositories --repository-names pencil-shorts --region "$REGION" 2>/dev/null || \
  aws ecr create-repository --repository-name pencil-shorts --region "$REGION"
echo "  ✅ ECR hazır"

# ── 4. GitHub OIDC provider (hesapta bir kez) ───────────────────────────────
echo ""
echo "[4/5] GitHub OIDC provider kontrol ediliyor..."
aws iam list-open-id-connect-providers 2>/dev/null | grep -q "token.actions.githubusercontent.com" && \
  echo "  ✅ OIDC provider zaten var" || \
  aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 && \
  echo "  ✅ OIDC provider oluşturuldu"

# ── 5. Terraform init ────────────────────────────────────────────────────────
echo ""
echo "[5/5] Terraform init..."
cd "$(dirname "$0")"
terraform init
echo "  ✅ Terraform hazır"

echo ""
echo "=== Bootstrap tamamlandı ==="
echo ""
echo "Sıradaki adımlar:"
echo "1. terraform plan -var='budget_alert_email=senin@email.com'"
echo "2. Planı gözden geçir"
echo "3. terraform apply -var='budget_alert_email=senin@email.com'"
echo "4. Output'taki github_actions_role_arn değerini GitHub repo Secrets'a ekle:"
echo "   Settings → Secrets → AWS_DEPLOY_ROLE_ARN"
echo "5. BUDGET_ALERT_EMAIL secret'ını da ekle"
echo "6. GitHub Actions environment 'production' oluştur, required reviewer ekle"
