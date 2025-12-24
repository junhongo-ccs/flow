# GitHub Secrets設定手順

このプロジェクトのCI/CDを動作させるために、以下のGitHub Secretsを設定する必要があります。

## 必要なSecrets

### Azure認証用 (OIDC)
- `AZURE_CLIENT_ID`: Azure ADアプリケーションのクライアントID
- `AZURE_TENANT_ID`: AzureテナントID
- `AZURE_SUBSCRIPTION_ID`: AzureサブスクリプションID

### Azure OpenAI
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAIのエンドポイントURL
  - 例: `https://your-resource.openai.azure.com/`
- `AZURE_OPENAI_API_KEY`: Azure OpenAIのAPIキー

### Azure AI Search
- `AZURE_AI_SEARCH_ENDPOINT`: Azure AI SearchのエンドポイントURL
  - 例: `https://your-search.search.windows.net`
- `AZURE_AI_SEARCH_API_KEY`: Azure AI SearchのAPIキー

## 設定方法

1. GitHubリポジトリページを開く
2. **Settings** → **Secrets and variables** → **Actions** に移動
3. **New repository secret** をクリック
4. 上記の各Secretを追加

## 確認方法

Secretsが正しく設定されているか確認するには:

```bash
# GitHub Actionsの「Prompt Flow Test」ワークフローを実行
# "Verify Secrets" ステップでシークレットの長さが表示されます
```

## ローカル開発用

ローカルで開発する場合は、`.env`ファイルを作成してください:

```bash
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

**注意**: `.env`ファイルは`.gitignore`に含まれており、Gitにコミットされません。
