#!/bin/bash
# Azure OIDC認証設定スクリプト
# このスクリプトを実行すると、GitHub Actions用のAzure OIDC認証が自動的に設定されます

set -e  # エラーが発生したら停止

echo "🚀 Azure OIDC認証設定を開始します..."
echo ""

# 1. アプリケーション名を設定
APP_NAME="github-actions-flow-deploy"
GITHUB_ORG="junhongo-ccs"
GITHUB_REPO="flow"
RESOURCE_GROUP="rg-estimation-agent"

echo "📝 設定内容:"
echo "  アプリケーション名: $APP_NAME"
echo "  GitHubリポジトリ: $GITHUB_ORG/$GITHUB_REPO"
echo "  リソースグループ: $RESOURCE_GROUP"
echo ""

# 2. Azure ADアプリケーションを作成
echo "1️⃣  Azure ADアプリケーションを作成中..."
APP_ID=$(az ad app create --display-name $APP_NAME --query appId -o tsv)
echo "   ✅ 作成完了: $APP_ID"
echo ""

# 3. サブスクリプション情報を取得
echo "2️⃣  Azureサブスクリプション情報を取得中..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "   ✅ サブスクリプションID: $SUBSCRIPTION_ID"
echo "   ✅ テナントID: $TENANT_ID"
echo ""

# 4. サービスプリンシパルを作成
echo "3️⃣  サービスプリンシパルを作成中..."
az ad sp create --id $APP_ID > /dev/null
echo "   ✅ 作成完了"
echo ""

# 5. ロールを付与
echo "4️⃣  Contributorロールを付与中..."
az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  > /dev/null
echo "   ✅ ロール付与完了"
echo ""

# 6. Federated Credentialを作成
echo "5️⃣  Federated Credentialを作成中..."
az ad app federated-credential create \
  --id $APP_ID \
  --parameters "{
    \"name\": \"github-actions-main\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:$GITHUB_ORG/$GITHUB_REPO:ref:refs/heads/main\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }" > /dev/null
echo "   ✅ Federated Credential作成完了"
echo ""

# 7. 結果を表示
echo "✨ 設定が完了しました！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 以下の値をGitHub Secretsに設定してください:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "AZURE_CLIENT_ID=$APP_ID"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 GitHub Secretsの設定ページ:"
echo "   https://github.com/$GITHUB_ORG/$GITHUB_REPO/settings/secrets/actions"
echo ""
echo "💡 次のステップ:"
echo "   1. 上記のURLにアクセス"
echo "   2. 'New repository secret' をクリック"
echo "   3. 上記の3つのSecretsを追加"
echo "   4. GitHub Actionsの 'Deploy Prompt Flow to Azure' を実行"
echo ""
