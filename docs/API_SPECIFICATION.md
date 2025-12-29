# AI見積もりシステム - API仕様書

**バージョン**: 1.0  
**最終更新**: 2025-12-30

---

## 📋 概要

AI見積もりシステムは、開発プロジェクトの見積もりとデザイン相談を提供するAPIです。Azure OpenAI（gpt-4o）を使用して、ユーザーの入力に基づいた詳細な見積もりとアドバイスを生成します。

---

## 🌐 エンドポイント一覧

### 1. AI Agent API

**ベースURL**: `https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io`

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/health` | GET | ヘルスチェック |
| `/score` | POST | 見積もり・相談の実行 |

### 2. Backend Calc API

**ベースURL**: `https://estimate-api-cli.azurewebsites.net/api`

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/calc` | POST | 見積もり計算 |

---

## 🔌 API詳細

### ヘルスチェック

#### リクエスト

```http
GET /health
Host: estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io
```

#### レスポンス

**成功時（200 OK）**:
```json
{
  "status": "healthy"
}
```

---

### 見積もり・相談の実行

AI Agentに見積もりまたはデザイン相談を依頼します。

#### リクエスト

```http
POST /score
Host: estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io
Content-Type: application/json
```

#### リクエストボディ

##### パターン1: 開発見積もり

```json
{
  "user_input": {
    "inquiry_type": "development_estimate",
    "project_type": "web_app",
    "duration_months": 6,
    "team_size": 3
  }
}
```

**フィールド説明**:

| フィールド | 型 | 必須 | 説明 | 有効な値 |
|-----------|---|------|------|---------|
| `inquiry_type` | string | ✅ | 問い合わせタイプ | `"development_estimate"` |
| `project_type` | string | ✅ | プロジェクトタイプ | `"web_app"`, `"mobile_app"`, `"desktop_app"` |
| `duration_months` | integer | ✅ | 開発期間（月） | 1以上の整数 |
| `team_size` | integer | ✅ | チームサイズ（人） | 1以上の整数 |

##### パターン2: デザイン相談

```json
{
  "user_input": {
    "inquiry_type": "design_consultation",
    "design_phase": {
      "wireframe_ready": true,
      "design_company_selected": false,
      "figma_experience": "none",
      "screen_count": 20,
      "responsive_required": true
    }
  }
}
```

**フィールド説明**:

| フィールド | 型 | 必須 | 説明 | 有効な値 |
|-----------|---|------|------|---------|
| `inquiry_type` | string | ✅ | 問い合わせタイプ | `"design_consultation"` |
| `design_phase.wireframe_ready` | boolean | ✅ | ワイヤーフレーム準備済み | `true`, `false` |
| `design_phase.design_company_selected` | boolean | ✅ | デザイン会社選定済み | `true`, `false` |
| `design_phase.figma_experience` | string | ✅ | Figma経験 | `"none"`, `"beginner"`, `"intermediate"`, `"advanced"` |
| `design_phase.screen_count` | integer | ✅ | 画面数 | 1以上の整数 |
| `design_phase.responsive_required` | boolean | ✅ | レスポンシブ対応必要 | `true`, `false` |

#### レスポンス

**成功時（200 OK）**:

```json
{
  "response": "見積もり結果をお知らせします。\n\n**総計**: **1,848,000 JPY**\n\n内訳:\n- 基本開発費用: 1,680,000 JPY\n- 画面単価: 120,000 JPY\n- 難易度係数: 1.0（標準）\n- バッファ係数: 1.1（リスク管理のため）\n\nこの見積もりは、14画面のWebアプリケーションを対象としており..."
}
```

**フィールド説明**:

| フィールド | 型 | 説明 |
|-----------|---|------|
| `response` | string | AI生成の見積もり結果またはアドバイス（Markdown形式） |

**エラー時（500 Internal Server Error）**:

```json
{
  "error": "Connection error."
}
```

または

```json
{
  "error": "詳細なエラーメッセージ"
}
```

---

## 🔧 Backend Calc API

### 見積もり計算

プロジェクトの見積もりを計算します。

#### リクエスト

```http
POST /calc
Host: estimate-api-cli.azurewebsites.net/api
Content-Type: application/json
```

#### リクエストボディ

```json
{
  "project_type": "web_app",
  "duration_months": 6,
  "team_size": 3
}
```

**フィールド説明**:

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `project_type` | string | ✅ | プロジェクトタイプ |
| `duration_months` | integer | ✅ | 開発期間（月） |
| `team_size` | integer | ✅ | チームサイズ（人） |

#### レスポンス

**成功時（200 OK）**:

```json
{
  "total_cost": 1848000,
  "base_cost": 1680000,
  "screen_unit_price": 120000,
  "difficulty_factor": 1.0,
  "buffer_factor": 1.1,
  "estimated_screens": 14
}
```

---

## 🔐 認証

現在、すべてのエンドポイントは**認証不要**です。

- API Keyは不要
- CORS有効（すべてのオリジンからアクセス可能）

---

## 🌍 CORS設定

すべてのエンドポイントでCORSが有効化されています。

```http
Access-Control-Allow-Origin: *
```

ブラウザからの直接アクセスが可能です。

---

## 📊 レート制限

現在、レート制限は設定されていません。

---

## 🔄 システムアーキテクチャ

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTPS POST /score
       ▼
┌─────────────────────────────────────┐
│      AI Agent (Container Apps)      │
│  - Flask アプリ                      │
│  - CORS有効                          │
└────┬────────────┬──────────┬────────┘
     │            │          │
     │ call_calc  │ RAG      │ LLM
     ▼            ▼          ▼
┌──────────┐ ┌─────────┐ ┌──────────┐
│ Backend  │ │ Azure   │ │ Azure    │
│ Calc API │ │ AI      │ │ OpenAI   │
│          │ │ Search  │ │ (gpt-4o) │
└──────────┘ └─────────┘ └──────────┘
```

---

## 📝 使用例

### cURLでの使用例

#### 開発見積もり

```bash
curl -X POST https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io/score \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "inquiry_type": "development_estimate",
      "project_type": "web_app",
      "duration_months": 6,
      "team_size": 3
    }
  }'
```

#### デザイン相談

```bash
curl -X POST https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io/score \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "inquiry_type": "design_consultation",
      "design_phase": {
        "wireframe_ready": true,
        "design_company_selected": false,
        "figma_experience": "none",
        "screen_count": 20,
        "responsive_required": true
      }
    }
  }'
```

### JavaScriptでの使用例

```javascript
// 開発見積もり
const response = await fetch('https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io/score', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_input: {
      inquiry_type: 'development_estimate',
      project_type: 'web_app',
      duration_months: 6,
      team_size: 3
    }
  })
});

const result = await response.json();
console.log(result.response);
```

### Pythonでの使用例

```python
import requests

# 開発見積もり
url = "https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io/score"
payload = {
    "user_input": {
        "inquiry_type": "development_estimate",
        "project_type": "web_app",
        "duration_months": 6,
        "team_size": 3
    }
}

response = requests.post(url, json=payload)
result = response.json()
print(result["response"])
```

---

## ⚠️ エラーハンドリング

### HTTPステータスコード

| コード | 説明 |
|-------|------|
| 200 | 成功 |
| 400 | リクエストが不正 |
| 500 | サーバーエラー |

### エラーレスポンスの例

```json
{
  "error": "Connection error."
}
```

エラーが発生した場合、`error`フィールドにエラーメッセージが含まれます。

---

## 🔍 デバッグ

### ヘルスチェックの確認

```bash
curl https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io/health
```

期待される応答:
```json
{"status": "healthy"}
```

### レスポンス時間

通常、レスポンスには5〜15秒かかります（AI生成のため）。

---

## 📚 関連リソース

- **Frontend UI**: https://zealous-river-0efdffa0f.1.azurestaticapps.net
- **GitHubリポジトリ**:
  - AI Agent: https://github.com/junhongo-ccs/flow
  - Frontend UI: https://github.com/junhongo-ccs/estimation-ui-app
  - Backend Calc: https://github.com/junhongo-ccs/estimate-backend-calc

---

## 📞 サポート

質問や問題がある場合は、GitHubリポジトリのIssuesセクションをご利用ください。

---

**最終更新**: 2025-12-30  
**バージョン**: 1.0
