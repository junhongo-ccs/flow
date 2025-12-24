# Azure OIDC認証設定手順

GitHub ActionsからAzureへのデプロイを自動化するために、OIDC（OpenID Connect）認証を設定する必要があります。

## 前提条件
- Azure CLI がインストールされていること
- Azureサブスクリプションへの管理者権限があること

## 手順

### 1. Azure ADアプリケーションの作成

```bash
# アプリケーション名を設定
APP_NAME="github-actions-flow-deploy"

# Azure ADアプリケーションを作成
az ad app create --display-name $APP_NAME
```

作成されたアプリケーションの `appId` (Client ID) をメモしてください。

### 2. サービスプリンシパルの作成

```bash
# 上記で取得したappIdを使用
APP_ID="<your-app-id>"

# サブスクリプションIDを取得
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# サービスプリンシパルを作成し、Contributorロールを付与
az ad sp create-for-rbac \
  --name $APP_NAME \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-estimation-agent \
  --sdk-auth
```

### 3. Federated Credentialの設定

```bash
# GitHubリポジトリ情報
GITHUB_ORG="junhongo-ccs"
GITHUB_REPO="flow"

# Federated Credentialを作成（mainブランチ用）
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'$GITHUB_ORG'/'$GITHUB_REPO':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### 4. 必要な情報の取得

以下の情報を取得し、GitHub Secretsに設定します:

```bash
# Client ID (Application ID)
echo "AZURE_CLIENT_ID: $APP_ID"

# Tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "AZURE_TENANT_ID: $TENANT_ID"

# Subscription ID
echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
```

### 5. GitHub Secretsへの設定

1. GitHubリポジトリページを開く: https://github.com/junhongo-ccs/flow
2. **Settings** → **Secrets and variables** → **Actions** に移動
3. 以下のSecretsを追加:
   - `AZURE_CLIENT_ID`: 上記で取得したClient ID
   - `AZURE_TENANT_ID`: 上記で取得したTenant ID
   - `AZURE_SUBSCRIPTION_ID`: 上記で取得したSubscription ID

### 6. 動作確認

GitHub Actionsの「Deploy Prompt Flow to Azure」ワークフローを手動実行して、デプロイが成功することを確認します。

## トラブルシューティング

### エラー: "Not all values are present"
- GitHub Secretsが正しく設定されているか確認
- Secret名のスペルミスがないか確認

### エラー: "Login failed"
- Federated Credentialが正しく設定されているか確認
- リポジトリ名、ブランチ名が正しいか確認

## 参考資料
- [Azure OIDC with GitHub Actions](https://learn.microsoft.com/azure/developer/github/connect-from-azure)
- [GitHub Actions: Azure Login](https://github.com/Azure/login)
