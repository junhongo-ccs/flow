# Azure OIDC認証設定手順

GitHub ActionsからAzureへのデプロイを自動化するために、OIDC（OpenID Connect）認証を設定する必要があります。

## クイックスタート（推奨）

**最も簡単な方法**: 自動セットアップスクリプトを使用

```bash
cd /Users/hongoujun/Documents/GitHub/flow
./scripts/setup-azure-oidc.sh
```

このスクリプトが以下をすべて自動で実行します:
1. Azure ADアプリケーション作成
2. サービスプリンシパル作成
3. ロール付与
4. Federated Credential設定
5. GitHub Secretsに設定すべき値を表示

スクリプト実行後、表示された3つの値をGitHub Secretsに設定するだけです。

---

## 手動セットアップ手順

自動スクリプトを使わない場合は、以下の手順を実行してください。

## 前提条件
- Azure CLI がインストールされていること
- Azureサブスクリプションへの管理者権限があること

## 手順

### 1. Azure ADアプリケーションの作成

```bash
# アプリケーション名を設定
APP_NAME="github-actions-flow-deploy"

# Azure ADアプリケーションを作成し、appIdを取得
APP_ID=$(az ad app create --display-name $APP_NAME --query appId -o tsv)

# 取得したClient IDを表示
echo "AZURE_CLIENT_ID: $APP_ID"
```

> **💡 ヒント**: `APP_ID`変数に自動的にClient IDが格納されます。この値は後の手順で使用します。

### 2. サービスプリンシパルの作成

```bash
# サブスクリプションIDを取得
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# サービスプリンシパルを作成し、Contributorロールを付与
# 注: APP_IDは前のステップで既に設定されています
az ad sp create --id $APP_ID

# リソースグループへのContributorロールを付与
az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-estimation-agent

echo "サービスプリンシパルの作成が完了しました"
```

> **📝 注意**: `--sdk-auth`オプションは非推奨のため、OIDC認証を使用します。

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
