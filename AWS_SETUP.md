# AWS_SETUP.md — Tüm AWS yapılandırması (aws CLI, sırayla)

> Claude Code: Bu dosyadaki komutları **yukarıdan aşağıya sırayla** çalıştır.
> 🧑 = insandan değer/onay iste (auth, sır değerleri, maliyet onayı).
> 🤖 = sen otomatik çalıştır. Her bölüm sonunda kısa özet ver, devam onayı al.
> Sır değerlerini ASLA repoya/log'a yazma — sadece SSM'e.

Mimari: EventBridge Scheduler → günde 1 kez → ECS **Fargate Spot** tek-shot görev
(bu depo imajı). Boşta maliyet $0. Sırlar SSM'de. Loglar CloudWatch'ta.

---

## 0. 🧑 Önkoşul — auth (insan yapar, Claude Code çalıştıramaz)
```bash
aws configure          # veya: aws configure sso
aws sts get-caller-identity   # doğrula
```

---

## 1. 🤖 Değişkenler (bir kez ayarla; aynı kabukta devam et)
```bash
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export PROJECT=pencil-shorts
export ECR_REPO=$PROJECT
export BUCKET=${PROJECT}-${ACCOUNT_ID}        # global benzersiz olmalı
export LOG_GROUP=/ecs/$PROJECT
export CLUSTER=$PROJECT
export TASK_FAMILY=$PROJECT
export GITHUB_REPO=osmsakli/pencil-shorts     # OIDC için
echo "ACCOUNT=$ACCOUNT_ID REGION=$AWS_REGION BUCKET=$BUCKET"
```

---

## 2. 🤖 ECR (imaj deposu)
```bash
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION \
  --image-scanning-configuration scanOnPush=true 2>/dev/null || echo "ECR zaten var"
export ECR_URI=$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO
echo $ECR_URI
```

İmajı derle + push (EC2/lokal Docker ile; repo kökünde):
```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -t $ECR_URI:latest .
docker push $ECR_URI:latest
```

---

## 3. 🤖 S3 (opsiyonel arşiv / gelecekteki state)
```bash
if [ "$AWS_REGION" = "us-east-1" ]; then
  aws s3api create-bucket --bucket $BUCKET --region $AWS_REGION 2>/dev/null || echo "bucket var"
else
  aws s3api create-bucket --bucket $BUCKET --region $AWS_REGION \
    --create-bucket-configuration LocationConstraint=$AWS_REGION 2>/dev/null || echo "bucket var"
fi
aws s3api put-public-access-block --bucket $BUCKET \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket $BUCKET --versioning-configuration Status=Enabled
```

---

## 4. 🧑 Sırlar → SSM Parameter Store (değerleri insan girer)
```bash
# ANTHROPIC anahtarı (LLM)
aws ssm put-parameter --name /$PROJECT/anthropic_api_key --type SecureString --overwrite \
  --value "BURAYA_ANTHROPIC_ANAHTARI"
# upload-post anahtarı (yayınlama)
aws ssm put-parameter --name /$PROJECT/upload_post_api_key --type SecureString --overwrite \
  --value "BURAYA_UPLOAD_POST_ANAHTARI"
# Affiliate linki (açıklamaya eklenir) — yoksa boş bırak
aws ssm put-parameter --name /$PROJECT/affiliate_link --type SecureString --overwrite \
  --value "https://senin-affiliate-linkin"
```

---

## 5. 🤖 CloudWatch log grubu
```bash
aws logs create-log-group --log-group-name $LOG_GROUP 2>/dev/null || echo "log grubu var"
aws logs put-retention-policy --log-group-name $LOG_GROUP --retention-in-days 30
```

---

## 6. 🤖 IAM rolleri

### 6a. ECS task execution role (imaj çekme, log, SSM okuma)
```bash
cat > /tmp/ecs-trust.json <<'JSON'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
"Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}
JSON

aws iam create-role --role-name ${PROJECT}-exec --assume-role-policy-document file:///tmp/ecs-trust.json 2>/dev/null || echo "exec rol var"
aws iam attach-role-policy --role-name ${PROJECT}-exec \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

cat > /tmp/exec-ssm.json <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["ssm:GetParameters"],
  "Resource":"arn:aws:ssm:$AWS_REGION:$ACCOUNT_ID:parameter/$PROJECT/*"},
 {"Effect":"Allow","Action":["kms:Decrypt"],
  "Resource":"arn:aws:kms:$AWS_REGION:$ACCOUNT_ID:alias/aws/ssm"}]}
JSON
aws iam put-role-policy --role-name ${PROJECT}-exec --policy-name ssm-read --policy-document file:///tmp/exec-ssm.json
export EXEC_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/${PROJECT}-exec
```

### 6b. ECS task role (uygulamanın izinleri: S3 yazma — opsiyonel)
```bash
aws iam create-role --role-name ${PROJECT}-task --assume-role-policy-document file:///tmp/ecs-trust.json 2>/dev/null || echo "task rol var"
cat > /tmp/task-s3.json <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:PutObject","s3:GetObject","s3:ListBucket"],
  "Resource":["arn:aws:s3:::$BUCKET","arn:aws:s3:::$BUCKET/*"]}]}
JSON
aws iam put-role-policy --role-name ${PROJECT}-task --policy-name s3-rw --policy-document file:///tmp/task-s3.json
export TASK_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/${PROJECT}-task
```

### 6c. EventBridge Scheduler rolü (görevi tetikler)
```bash
cat > /tmp/sched-trust.json <<'JSON'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
"Principal":{"Service":"scheduler.amazonaws.com"},"Action":"sts:AssumeRole"}]}
JSON
aws iam create-role --role-name ${PROJECT}-scheduler --assume-role-policy-document file:///tmp/sched-trust.json 2>/dev/null || echo "scheduler rol var"
cat > /tmp/sched-run.json <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["ecs:RunTask"],"Resource":"*"},
 {"Effect":"Allow","Action":["iam:PassRole"],
  "Resource":["$EXEC_ROLE_ARN","$TASK_ROLE_ARN"]}]}
JSON
aws iam put-role-policy --role-name ${PROJECT}-scheduler --policy-name run-task --policy-document file:///tmp/sched-run.json
export SCHED_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/${PROJECT}-scheduler
```

---

## 7. 🤖 ECS cluster + task definition
```bash
aws ecs create-cluster --cluster-name $CLUSTER \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 2>/dev/null || echo "cluster var"
```

Task definition (üret → kaydet). İmaj içinde awscli olmadığından S3'e yazmaz; sadece
üretir + yayınlar:
```bash
cat > /tmp/taskdef.json <<JSON
{
 "family": "$TASK_FAMILY",
 "networkMode": "awsvpc",
 "requiresCompatibilities": ["FARGATE"],
 "cpu": "2048", "memory": "4096",
 "executionRoleArn": "$EXEC_ROLE_ARN",
 "taskRoleArn": "$TASK_ROLE_ARN",
 "containerDefinitions": [{
   "name": "app",
   "image": "$ECR_URI:latest",
   "essential": true,
   "entryPoint": ["/bin/bash","-lc"],
   "command": ["python3 pipeline/run.py --auto && python3 publish/upload.py --platforms tiktok youtube instagram"],
   "environment": [
     {"name":"TTS_PROVIDER","value":"edge"},
     {"name":"RHUBARB_RECOGNIZER","value":"phonetic"},
     {"name":"AFFILIATE_CTA","value":"👇 Beğendiysen kanala göz at"}
   ],
   "secrets": [
     {"name":"ANTHROPIC_API_KEY","valueFrom":"arn:aws:ssm:$AWS_REGION:$ACCOUNT_ID:parameter/$PROJECT/anthropic_api_key"},
     {"name":"UPLOAD_POST_API_KEY","valueFrom":"arn:aws:ssm:$AWS_REGION:$ACCOUNT_ID:parameter/$PROJECT/upload_post_api_key"},
     {"name":"AFFILIATE_LINK","valueFrom":"arn:aws:ssm:$AWS_REGION:$ACCOUNT_ID:parameter/$PROJECT/affiliate_link"}
   ],
   "logConfiguration": {
     "logDriver":"awslogs",
     "options":{"awslogs-group":"$LOG_GROUP","awslogs-region":"$AWS_REGION","awslogs-stream-prefix":"app"}
   }
 }]
}
JSON
aws ecs register-task-definition --cli-input-json file:///tmp/taskdef.json
export TASKDEF_ARN=$(aws ecs describe-task-definition --task-definition $TASK_FAMILY --query 'taskDefinition.taskDefinitionArn' --output text)
echo $TASKDEF_ARN
```

---

## 8. 🤖 Ağ (default VPC subnet + güvenlik grubu)
```bash
export SUBNETS=$(aws ec2 describe-subnets --filters Name=default-for-az,Values=true \
  --query 'Subnets[].SubnetId' --output text | tr '\t' ',')
export SG=$(aws ec2 describe-security-groups --filters Name=group-name,Values=default \
  --query 'SecurityGroups[0].GroupId' --output text)
echo "SUBNETS=$SUBNETS  SG=$SG"
```

---

## 9. 🤖 Önce ELLE TEST (zamanlamadan önce çalışıyor mu?)  🧑 ilk yüklemeyi onayla
```bash
aws ecs run-task --cluster $CLUSTER \
  --capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 \
  --task-definition $TASK_FAMILY \
  --count 1 \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=ENABLED}"
# Logları izle:
aws logs tail $LOG_GROUP --follow
```
> İlk denemede `publish/upload.py`'yi private/test moduna al, video doğru yüklendi mi gör.

---

## 10. 🤖 Günlük zamanlama (EventBridge Scheduler)
```bash
cat > /tmp/target.json <<JSON
{
 "Arn": "arn:aws:ecs:$AWS_REGION:$ACCOUNT_ID:cluster/$CLUSTER",
 "RoleArn": "$SCHED_ROLE_ARN",
 "EcsParameters": {
   "TaskDefinitionArn": "$TASKDEF_ARN",
   "TaskCount": 1,
   "LaunchType": "FARGATE",
   "CapacityProviderStrategy": [{"capacityProvider":"FARGATE_SPOT","weight":1}],
   "NetworkConfiguration": {
     "awsvpcConfiguration": {
       "Subnets": ["${SUBNETS//,/\",\"}"],
       "SecurityGroups": ["$SG"],
       "AssignPublicIp": "ENABLED"
     }
   }
 }
}
JSON
aws scheduler create-schedule --name ${PROJECT}-daily \
  --schedule-expression "cron(0 14 * * ? *)" \
  --schedule-expression-timezone "Europe/Istanbul" \
  --flexible-time-window "Mode=OFF" \
  --target file:///tmp/target.json 2>/dev/null \
  || aws scheduler update-schedule --name ${PROJECT}-daily \
       --schedule-expression "cron(0 14 * * ? *)" \
       --schedule-expression-timezone "Europe/Istanbul" \
       --flexible-time-window "Mode=OFF" \
       --target file:///tmp/target.json
```
> `cron(0 14 ...)` = her gün saat 14:00 (İstanbul). İstediğin saate çek.

---

## 11. 🤖 Bütçe alarmı ($20/ay güvenlik ağı)
```bash
cat > /tmp/budget.json <<JSON
{"BudgetName":"${PROJECT}-monthly","BudgetLimit":{"Amount":"20","Unit":"USD"},
 "TimeUnit":"MONTHLY","BudgetType":"COST"}
JSON
cat > /tmp/notify.json <<JSON
[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN",
  "Threshold":80,"ThresholdType":"PERCENTAGE"},
  "Subscribers":[{"SubscriptionType":"EMAIL","Address":"osmsakli@gmail.com"}]}]
JSON
aws budgets create-budget --account-id $ACCOUNT_ID \
  --budget file:///tmp/budget.json --notifications-with-subscribers file:///tmp/notify.json 2>/dev/null || echo "bütçe var"
```

---

## 12. 🤖 (Opsiyonel) GitHub Actions için OIDC + CI rolü
```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 2>/dev/null || echo "OIDC var"

cat > /tmp/ci-trust.json <<JSON
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Federated":"arn:aws:iam::$ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"},
 "Action":"sts:AssumeRoleWithWebIdentity",
 "Condition":{"StringEquals":{"token.actions.githubusercontent.com:aud":"sts.amazonaws.com"},
 "StringLike":{"token.actions.githubusercontent.com:sub":"repo:$GITHUB_REPO:*"}}}]}
JSON
aws iam create-role --role-name ${PROJECT}-ci --assume-role-policy-document file:///tmp/ci-trust.json 2>/dev/null || echo "CI rol var"

cat > /tmp/ci-perms.json <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["ecr:GetAuthorizationToken"],"Resource":"*"},
 {"Effect":"Allow","Action":["ecr:BatchCheckLayerAvailability","ecr:PutImage","ecr:InitiateLayerUpload","ecr:UploadLayerPart","ecr:CompleteLayerUpload","ecr:BatchGetImage"],
  "Resource":"arn:aws:ecr:$AWS_REGION:$ACCOUNT_ID:repository/$ECR_REPO"},
 {"Effect":"Allow","Action":["ecs:RegisterTaskDefinition","ecs:RunTask","ecs:DescribeTaskDefinition"],"Resource":"*"},
 {"Effect":"Allow","Action":["iam:PassRole"],"Resource":["$EXEC_ROLE_ARN","$TASK_ROLE_ARN"]}]}
JSON
aws iam put-role-policy --role-name ${PROJECT}-ci --policy-name ci --policy-document file:///tmp/ci-perms.json
echo "CI rol ARN: arn:aws:iam::$ACCOUNT_ID:role/${PROJECT}-ci  (GitHub Actions'a bunu ver)"
```

---

## 13. Operasyon
```bash
# Manuel tetik (şimdi bir video üret):
aws ecs run-task --cluster $CLUSTER --task-definition $TASK_FAMILY --count 1 \
  --capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=ENABLED}"

# Logları gör:
aws logs tail $LOG_GROUP --since 1h --follow

# KILL SWITCH (üretimi durdur):
aws scheduler update-schedule --name ${PROJECT}-daily --state DISABLED \
  --schedule-expression "cron(0 14 * * ? *)" --flexible-time-window "Mode=OFF" --target file:///tmp/target.json

# Yeni imaj sonrası task def güncelle: 7. adımı tekrar çalıştır (register-task-definition).
```

---

## Guardrail (Claude Code)
1. Sır değerleri yalnızca SSM (4. adım) — koda/log'a/repoya asla.
2. 9. ve 10. adım (gerçek yükleme + zamanlama) öncesi 🧑 onay al; 11. bütçeyi erken kur.
3. İlk yüklemeyi private/test modda doğrula, sonra public.
4. Her bölümde dur, özetle, devam onayı al. Mevcut AWS kaynaklarına dokunma.
