# AI見積もりシステム開発 - 技術メモ（内部用）

**作成日**: 2025年12月24日  
**作成者**: 本郷 純  
**目的**: 開発過程の記録と今後の参考資料

---

## 1. プロジェクト構成

### リポジトリ構成

```
estimate-backend-calc/     # Backend 計算API
├── function_app.py        # Azure Functions エントリポイント
├── config.yaml            # 計算係数設定
└── .github/workflows/     # CI/CD

flow/                      # AI Agent (Prompt Flow)
├── estimation_agent/
│   ├── flow.dag.yaml      # Agent定義
│   ├── call_calc_tool.py  # Backend API呼び出し
│   ├── lookup_knowledge.py # RAG検索
│   └── generate_response.jinja2 # LLMプロンプト
└── .github/workflows/     # CI/CD

estimation-ui-app/         # Frontend UI（未実装）
```

### Azure リソース

| リソース | 名前 | 用途 | 状態 |
|---------|------|------|------|
| Resource Group | `rg-estimation-agent` | 全リソース管理 | ✅ |
| Azure Functions | `estimate-api-cli` | Backend API | ✅ 稼働中 |
| Azure AI Foundry | `mlw-estimation-agent` | AI Agent実行環境 | ✅ |
| Azure OpenAI | `estimation-openai` | GPT-4o | ✅ |
| Azure AI Search | `estimation-search` | RAG検索 | ✅ |
| Online Endpoint | `estimation-agent-endpoint` | Agent公開 | 🔄 デプロイ中 |

---

## 2. 実装完了項目

### 2.1 Backend API (`estimate-backend-calc`)

**エンドポイント**: `https://estimate-api-cli.azurewebsites.net/api/calculate_estimate`

**リクエスト形式**:
```json
{
  "screen_count": 15,
  "complexity": "medium"
}
```

**レスポンス形式**:
```json
{
  "status": "ok",
  "estimated_amount": 18000000,
  "breakdown": {
    "development": 12600000,
    "design": 3600000,
    "management": 1800000
  }
}
```

**CI/CD**: GitHub Actions で自動デプロイ済み

---

### 2.2 AI Agent (`flow`)

**実装内容**:
- 3ノード構成: `call_calc` → `lookup_knowledge` → `generate_response`
- Azure OpenAI (gpt-4o) 統合
- Azure AI Search によるRAG実装（18種類のドキュメント）
- 入力形式の自動変換（ユーザー入力 → Backend API形式）

**環境変数**:
```bash
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_AI_SEARCH_ENDPOINT=...
AZURE_AI_SEARCH_API_KEY=...
USE_MOCK_CALC=false
CALC_API_URL=https://estimate-api-cli.azurewebsites.net/api
```

**CI/CD**: GitHub Actions + Azure OIDC認証

---

## 3. デプロイ問題のトラブルシューティング記録

### 問題1: コンテナクラッシュ（依存関係不足）

**発生日時**: 2025-12-24 午前  
**エラー**: `Liveness probe failed`

**原因**:
- `lookup_knowledge.py` で `azure-search-documents` を使用
- `requirements.txt` に記載なし
- コンテナ起動時に依存関係解決失敗

**解決策**:
```diff
# requirements.txt
+ azure-search-documents
+ azure-identity
```

**コミット**: `360051a`

---

### 問題2: デプロイメント名の競合

**発生日時**: 2025-12-24 午後  
**エラー**: `A deployment with this name already exists`

**原因**:
- 前回の失敗したデプロイメント `production` が残存
- ワークフローの削除ステップが不完全

**解決策**:
```yaml
# .github/workflows/deploy-prompt-flow.yml
- name: Delete existing production deployment
  run: |
    az ml online-deployment delete --name production --yes
```

**コミット**: `fe16809`

---

### 問題3: 削除完了前の作成試行

**発生日時**: 2025-12-24 午後  
**エラー**: 同上（問題2が再発）

**原因**:
- `--no-wait` フラグにより削除が非同期実行
- 削除完了前に作成ステップが実行

**解決策（第1版）**:
```bash
# --no-wait を削除（同期削除）
az ml online-deployment delete --name production --yes
```

**問題**: 同期削除が時間かかりすぎてタイムアウト

**解決策（第2版）**:
```bash
# --no-wait + 削除完了確認ループ
az ml online-deployment delete --name production --yes --no-wait

for i in {1..30}; do
  STILL_EXISTS=$(az ml online-deployment list ... --query "[?name=='production'].name")
  if [ -z "$STILL_EXISTS" ]; then
    break
  fi
  sleep 10
done
```

**コミット**: `002ae59`, `b04c97d`, `a8256f1`

---

### 問題4: Liveness Probe 設定不足

**発生日時**: 2025-12-24 午後  
**エラー**: `Liveness probe failed: Get "http://10.66.0.2:5001/": connection refused`

**原因**:
- Liveness Probe がデフォルトの `/` にアクセス
- Prompt Flow は `/health` エンドポイントを提供
- パス指定がないため接続失敗

**解決策**:
```yaml
liveness_probe:
  path: /health  # 追加
  initial_delay: 600
  period: 30
  timeout: 30
  failure_threshold: 30

readiness_probe:
  path: /health  # 追加
  initial_delay: 600
  period: 30
  timeout: 30
  failure_threshold: 30
```

**コミット**: `2574791`

**現在の状態**: デプロイ実行中（Run #10）

---

## 4. 学んだこと

### 4.1 Azure ML Online Deployment

- **削除は時間がかかる**: 同期削除は5-10分かかることがある
- **削除確認が重要**: `list` コマンドで存在確認が確実
- **Probe設定は必須**: デフォルトでは `/` にアクセスするため、明示的にパス指定が必要

### 4.2 Prompt Flow デプロイ

- **依存関係の完全性**: `requirements.txt` に全ての依存関係を記載
- **初期遅延の重要性**: コンテナ起動に時間がかかるため、600秒の初期遅延が必要
- **ヘルスチェック**: `/health` エンドポイントが標準で提供される

### 4.3 GitHub Actions

- **OIDC認証**: パスワードレス認証でセキュア
- **エラーハンドリング**: `continue-on-error: true` で削除失敗を許容
- **ループ処理**: Bash のループで削除完了を確認

---

## 5. 今後の改善点

### 5.1 デプロイメント戦略

**現在**: 毎回 `production` デプロイメントを削除→作成

**改善案**:
- Blue-Green デプロイメント
- デプロイメント名にバージョン番号を付与（例: `production-v1`, `production-v2`）
- トラフィックの段階的切り替え

### 5.2 監視・ロギング

**追加予定**:
- Application Insights 統合
- カスタムメトリクス
- アラート設定

### 5.3 コスト最適化

**PoC終了後**:
- Azure AI Search 削除（月額¥10,000削減）
- RAG機能無効化
- 月額¥500程度に削減

---

## 6. 参考資料

### ドキュメント

- システム仕様書: `docs/00_system_specification.md`
- 実装計画書: `docs/flows_implementation_plan.md`
- RAG削除手順: `brain/rag_removal_guide.md`
- コスト分析: `brain/cost_analysis_poc_vs_production.md`

### 外部リンク

- [Azure ML Online Endpoints](https://learn.microsoft.com/azure/machine-learning/how-to-deploy-online-endpoints)
- [Prompt Flow Documentation](https://microsoft.github.io/promptflow/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

---

## 7. 次のアクション

### 即座に実施

- [ ] デプロイ成功確認（Run #10）
- [ ] スコアリングURIの取得
- [ ] 疎通テスト実施

### 今週中

- [ ] Frontend UI 実装
- [ ] E2Eテスト
- [ ] デモ準備

### 来週以降

- [ ] パフォーマンス測定
- [ ] 運用マニュアル作成
- [ ] PoC レビュー実施
- [ ] RAG機能削除（レビュー後）

---

**最終更新**: 2025-12-24 15:40  
**次回更新予定**: デプロイ成功後
