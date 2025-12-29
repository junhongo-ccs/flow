# AI Agent 手動デプロイ手順

**作成日**: 2025-12-26  
**目的**: GitHub Actions でのデプロイが失敗する場合の手動デプロイ手順

---

## 前提条件

- Azure CLI がインストールされている
- Azure にログイン済み
- 必要な権限がある

---

## 手順

### 1. エンドポイントの削除（既存の場合）

```bash
# エンドポイントを削除
az ml online-endpoint delete \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent \
  --yes --no-wait

# 削除完了を確認（最大5分待機）
for i in {1..30}; do
  sleep 10
  ENDPOINT_EXISTS=$(az ml online-endpoint list \
    --resource-group rg-estimation-agent \
    --workspace-name mlw-estimation-agent \
    --query "[?name=='estimation-agent-endpoint'].name" -o tsv)
  
  if [ -z "$ENDPOINT_EXISTS" ]; then
    echo "✓ Endpoint deleted"
    break
  fi
  
  echo "⏳ Waiting for deletion... ($i/30)"
done
```

### 2. エンドポイントの作成

```bash
az ml online-endpoint create \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent
```

### 3. デプロイメント設定ファイルの準備

`estimation_agent/deployment/deployment.yaml` を確認:

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: production
endpoint_name: estimation-agent-endpoint
model:
  path: ..
instance_type: Standard_E2s_v3
instance_count: 1
environment:
  image: mcr.microsoft.com/azureml/curated/promptflow-runtime:latest
environment_variables:
  PRT_CONFIG_OVERRIDE: "deployment.subscription_id=...,deployment.resource_group=rg-estimation-agent,deployment.workspace_name=mlw-estimation-agent,deployment.endpoint_name=estimation-agent-endpoint,deployment.deployment_name=production"
  AZURE_OPENAI_ENDPOINT: "${AZURE_OPENAI_ENDPOINT}"
  AZURE_OPENAI_API_KEY: "${AZURE_OPENAI_API_KEY}"
  AZURE_AI_SEARCH_ENDPOINT: "${AZURE_AI_SEARCH_ENDPOINT}"
  AZURE_AI_SEARCH_API_KEY: "${AZURE_AI_SEARCH_API_KEY}"
  USE_MOCK_CALC: "false"
  CALC_API_URL: "https://estimate-api-cli.azurewebsites.net/api"
```

**重要**: `liveness_probe` と `readiness_probe` の設定は**含めない**こと！

### 4. 環境変数の設定

```bash
export AZURE_OPENAI_ENDPOINT="https://estimation-openai.openai.azure.com/"
export AZURE_OPENAI_API_KEY="YOUR_API_KEY"
export AZURE_AI_SEARCH_ENDPOINT="https://estimation-search.search.windows.net"
export AZURE_AI_SEARCH_API_KEY="YOUR_API_KEY"
```

または、`deployment.yaml` を直接編集して値を埋め込む。

### 5. デプロイメントの作成

```bash
cd estimation_agent

az ml online-deployment create \
  --file deployment/deployment.yaml \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent \
  --all-traffic
```

### 6. デプロイメント状況の確認

```bash
# デプロイメント一覧
az ml online-deployment list \
  --endpoint-name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent

# ログ確認
az ml online-deployment get-logs \
  --name production \
  --endpoint-name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent \
  --lines 100
```

### 7. スコアリングURIとAPIキーの取得

```bash
# スコアリングURI
az ml online-endpoint show \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent \
  --query scoring_uri -o tsv

# APIキー
az ml online-endpoint get-credentials \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent
```

---

## トラブルシューティング

### エラー: Liveness probe failed

**原因**: `deployment.yaml` に `liveness_probe` または `readiness_probe` の設定が含まれている

**解決策**: これらの設定を削除する

### エラー: User container has crashed

**原因**: 環境変数が正しく設定されていない、または依存関係が不足

**解決策**:
1. ログを確認: `az ml online-deployment get-logs ...`
2. 環境変数を確認
3. `requirements.txt` を確認

### デプロイメントが長時間 "Creating" 状態

**原因**: コンテナの起動に時間がかかっている（初回は10-15分）

**解決策**: 待つ。ログで進捗を確認。

---

## 成功の確認

```bash
# ヘルスチェック
curl -X GET "$(az ml online-endpoint show \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent \
  --query scoring_uri -o tsv)/health"

# テストリクエスト
curl -X POST "$(az ml online-endpoint show \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name mlw-estimation-agent \
  --query scoring_uri -o tsv)/score" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"user_input": {"project_type": "web_app", "duration_months": 6, "team_size": 3}}'
```

---

## 次のステップ

1. Frontend UI の `app.js` にスコアリングURIとAPIキーを設定
2. E2Eテスト
3. GitHub Actions ワークフローの修正（成功したら）
