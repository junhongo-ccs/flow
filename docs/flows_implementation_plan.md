# Flows実装プラン（確定版）

## 📋 前提条件

- **Azure環境**: これから構築
- **calc API**: 仕様は後で決定（モック実装から開始）
- **設計原則**: Agent中心設計を厳守

## 🎯 実装戦略

Azure環境が未構築のため、**ローカル開発→Azure展開** の段階的アプローチを採用します。

### 実装フェーズ概要

| Phase | 内容 | Azure依存 | 優先度 |
|-------|------|----------|--------|
| Phase 0 | ローカル開発環境構築 | ❌ なし | 🔴 最優先 |
| Phase 1 | Prompt Flow基本実装（モック） | ❌ なし | 🔴 最優先 |
| Phase 2 | テスト実装 | ❌ なし | 🟡 高 |
| Phase 3 | Azure環境構築 | ✅ あり | 🟢 中 |
| Phase 4 | Azure統合・デプロイ | ✅ あり | 🟢 中 |
| Phase 5 | CI/CD構築 | ✅ あり | ⚪ 低 |

---

## 📦 Phase 0: ローカル開発環境構築

**目的**: Azureなしでローカル開発できる環境を整備

### 必要なツール

```bash
# Python環境
python 3.11以上

# Prompt Flow CLI
pip install promptflow promptflow-tools promptflow-devkit

# 開発ツール
pip install pytest pytest-mock python-dotenv requests
```

### ディレクトリ構造

```
flows/
├── estimation_agent/
│   ├── flow.dag.yaml              # Flow定義
│   ├── call_calc_tool.py          # calc API呼び出しTool
│   ├── generate_response_mock.py  # レスポンス生成（モック版）
│   ├── requirements.txt           # 依存関係
│   ├── .env.example               # 環境変数テンプレート
│   └── .env                       # ローカル環境変数（gitignore）
├── tests/
│   ├── test_call_calc_tool.py     # Tool単体テスト
│   └── test_flow_local.py         # Flow統合テスト
├── .gitignore
└── README.md
```

### 実装タスク

- [ ] リポジトリ初期化
- [ ] `requirements.txt` 作成
- [ ] `.env.example` 作成
- [ ] `.gitignore` 設定

---

## 🔧 Phase 1: Prompt Flow基本実装（モック版）

**目的**: ローカルでFlowを動作させ、Agent中心設計を検証

### 1.1 Flow定義（flow.dag.yaml）

```yaml
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json
inputs:
  user_input:
    type: object
    description: "ユーザーからの見積もり依頼"

outputs:
  response:
    type: object
    reference: ${generate_response.output}

nodes:
  # ノード1: calc API呼び出し（モック）
  - name: call_calc
    type: python
    source:
      type: code
      path: call_calc_tool.py
    inputs:
      user_input: ${inputs.user_input}
  
  # ノード2: レスポンス生成（ローカルではモック、Azureでは LLM）
  - name: generate_response
    type: python
    source:
      type: code
      path: generate_response_mock.py
    inputs:
      calc_result: ${call_calc.output}
      user_input: ${inputs.user_input}
```

> [!IMPORTANT]
> **`aggregate_response.py` は不要と判断**
> 
> 理由:
> - 結果の統合は `generate_response` ノード（LLM）が行うべき
> - 単純なフォーマット変換なら、Jinja2テンプレートで十分
> - Agent の責務を分散させない

### 1.2 calc API呼び出しTool（call_calc_tool.py）

**モック実装版**（calc API仕様が決まるまで）

```python
from promptflow import tool
from typing import Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

@tool
def call_calc(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    calc APIを呼び出して計算結果を取得
    
    ローカル開発時はモックデータを返す
    本番環境では実際のAPIを呼び出す
    
    Args:
        user_input: ユーザー入力
            例: {
                "project_type": "web_app",
                "duration_months": 6,
                "team_size": 3
            }
    
    Returns:
        計算結果
            例: {
                "total": 10000000,
                "breakdown": {
                    "development": 7000000,
                    "design": 2000000,
                    "management": 1000000
                },
                "unit": "JPY"
            }
    """
    # 環境変数でモード切り替え
    use_mock = os.getenv("USE_MOCK_CALC", "true").lower() == "true"
    
    if use_mock:
        logger.info("Using mock calc API")
        return _mock_calc(user_input)
    else:
        logger.info("Calling real calc API")
        return _call_real_calc_api(user_input)

def _mock_calc(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """モック計算（開発用）"""
    # 簡易的な計算ロジック
    duration = user_input.get("duration_months", 6)
    team_size = user_input.get("team_size", 3)
    
    base_cost_per_month = 1000000  # 1人月100万円
    total = base_cost_per_month * duration * team_size
    
    return {
        "total": total,
        "breakdown": {
            "development": int(total * 0.7),
            "design": int(total * 0.2),
            "management": int(total * 0.1)
        },
        "unit": "JPY",
        "is_mock": True
    }

def _call_real_calc_api(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """実際のcalc API呼び出し（本番用）"""
    import requests
    
    calc_api_url = os.getenv("CALC_API_URL")
    api_key = os.getenv("CALC_API_KEY")
    
    if not calc_api_url:
        raise ValueError("CALC_API_URL is not set")
    
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["X-API-Key"] = api_key
    
    try:
        response = requests.post(
            f"{calc_api_url}/calculate",
            json=user_input,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"calc API error: {e}")
        return {
            "error": True,
            "message": str(e),
            "calc_result": None
        }
```

### 1.3 レスポンス生成（generate_response_mock.py）

**ローカル開発用のモック実装**

```python
from promptflow import tool
from typing import Dict, Any

@tool
def generate_response(calc_result: Dict[str, Any], user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    計算結果をもとにレスポンスを生成
    
    ローカル開発時はテンプレートベースのレスポンス
    Azure環境ではLLMを使用
    
    Args:
        calc_result: calc APIの結果
        user_input: ユーザー入力
    
    Returns:
        最終レスポンス
    """
    # エラーチェック
    if calc_result.get("error"):
        return {
            "success": False,
            "message": f"計算エラーが発生しました: {calc_result.get('message')}",
            "data": None
        }
    
    # 成功レスポンス生成
    total = calc_result.get("total", 0)
    breakdown = calc_result.get("breakdown", {})
    
    # テンプレートベースのレスポンス（後でLLMに置き換え）
    message = f"""見積もり結果をお知らせします。

【総額】
{total:,} 円

【内訳】"""
    
    for key, value in breakdown.items():
        message += f"\n- {key}: {value:,} 円"
    
    if calc_result.get("is_mock"):
        message += "\n\n※ これはモックデータです"
    
    return {
        "success": True,
        "message": message.strip(),
        "data": {
            "total": total,
            "breakdown": breakdown,
            "unit": calc_result.get("unit", "JPY")
        }
    }
```

### 1.4 環境変数設定

```bash
# .env.example
# calc API設定
USE_MOCK_CALC=true
CALC_API_URL=
CALC_API_KEY=

# Azure OpenAI設定（Phase 4で使用）
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 1.5 ローカル実行テスト

```bash
# Flow実行
pf flow test --flow estimation_agent --inputs user_input='{"project_type":"web_app","duration_months":6,"team_size":3}'

# インタラクティブモード
pf flow test --flow estimation_agent --interactive
```

### 実装タスク

- [ ] `flow.dag.yaml` 作成
- [ ] `call_calc_tool.py` 実装（モック版）
- [ ] `generate_response_mock.py` 実装
- [ ] `.env` 設定
- [ ] ローカル実行確認

---

## 🧪 Phase 2: テスト実装

**目的**: 品質を担保し、リファクタリングを安全に行う

### 2.1 Tool単体テスト

```python
# tests/test_call_calc_tool.py
import pytest
from call_calc_tool import call_calc, _mock_calc

def test_mock_calc_basic():
    """モック計算の基本動作"""
    user_input = {
        "project_type": "web_app",
        "duration_months": 6,
        "team_size": 3
    }
    
    result = _mock_calc(user_input)
    
    assert result["total"] == 18000000  # 100万 * 6ヶ月 * 3人
    assert result["breakdown"]["development"] == 12600000
    assert result["is_mock"] is True

def test_call_calc_with_mock_mode(monkeypatch):
    """モックモードでのcall_calc"""
    monkeypatch.setenv("USE_MOCK_CALC", "true")
    
    user_input = {"duration_months": 3, "team_size": 2}
    result = call_calc(user_input)
    
    assert result["is_mock"] is True
    assert result["total"] > 0

def test_call_calc_missing_params():
    """パラメータ不足時のデフォルト値"""
    result = _mock_calc({})
    
    assert result["total"] == 18000000  # デフォルト: 6ヶ月 * 3人
```

### 2.2 Flow統合テスト

```python
# tests/test_flow_local.py
import pytest
from promptflow import PFClient

@pytest.fixture
def pf_client():
    return PFClient()

def test_flow_basic_execution(pf_client):
    """Flow基本実行テスト"""
    result = pf_client.test(
        flow="estimation_agent",
        inputs={
            "user_input": {
                "project_type": "web_app",
                "duration_months": 6,
                "team_size": 3
            }
        }
    )
    
    assert result is not None
    assert result["success"] is True
    assert result["data"]["total"] > 0

def test_flow_with_minimal_input(pf_client):
    """最小限の入力でのテスト"""
    result = pf_client.test(
        flow="estimation_agent",
        inputs={
            "user_input": {}
        }
    )
    
    # デフォルト値で計算されることを確認
    assert result["success"] is True
```

### 実装タスク

- [ ] `test_call_calc_tool.py` 作成
- [ ] `test_flow_local.py` 作成
- [ ] テスト実行・合格確認
- [ ] カバレッジ確認

---

## ☁️ Phase 3: Azure環境構築

**目的**: Azure AI FoundryとAzure OpenAIの環境を準備

### 3.1 Azure AI Foundry プロジェクト作成

```bash
# Azure CLIでログイン
az login

# リソースグループ作成
az group create \
  --name rg-estimation-agent \
  --location eastus

# Azure AI Foundry プロジェクト作成
az ml workspace create \
  --name estimation-agent-workspace \
  --resource-group rg-estimation-agent \
  --location eastus
```

### 3.2 Azure OpenAI デプロイ

```bash
# Azure OpenAI リソース作成
az cognitiveservices account create \
  --name estimation-openai \
  --resource-group rg-estimation-agent \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# gpt-4o モデルデプロイ
az cognitiveservices account deployment create \
  --name estimation-openai \
  --resource-group rg-estimation-agent \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-05-13" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

### 3.3 接続情報の取得

```bash
# Azure OpenAI エンドポイント
az cognitiveservices account show \
  --name estimation-openai \
  --resource-group rg-estimation-agent \
  --query properties.endpoint

# API Key取得
az cognitiveservices account keys list \
  --name estimation-openai \
  --resource-group rg-estimation-agent
```

### 実装タスク

- [ ] Azureリソースグループ作成
- [ ] Azure AI Foundry プロジェクト作成
- [ ] Azure OpenAI リソース作成
- [ ] gpt-4o デプロイ
- [ ] 接続情報を `.env` に設定

---

## 🚀 Phase 4: Azure統合・デプロイ

**目的**: ローカル実装をAzure環境に統合

### 4.1 LLMノードへの置き換え

**`generate_response.jinja2` を作成**

```jinja2
system:
あなたは見積もりエージェントです。

ユーザーからの見積もり依頼に対して、calc APIの計算結果をもとに、分かりやすく説明してください。

## 計算結果
{{ calc_result | tojson }}

## 対応方針
- 計算結果を明確に提示
- 金額の根拠を説明
- 必要に応じて、次のステップを提案

{% if calc_result.error %}
エラーが発生しました。ユーザーに分かりやすく説明してください。
{% endif %}

user:
{{ user_input | tojson }}
```

**`flow.dag.yaml` を更新**

```yaml
nodes:
  - name: call_calc
    type: python
    source:
      type: code
      path: call_calc_tool.py
    inputs:
      user_input: ${inputs.user_input}
  
  # モック実装から LLM に変更
  - name: generate_response
    type: llm
    source:
      type: code
      path: generate_response.jinja2
    inputs:
      calc_result: ${call_calc.output}
      user_input: ${inputs.user_input}
    connection: azure_openai_connection
    api: chat
    parameters:
      deployment_name: gpt-4o
      temperature: 0.7
      max_tokens: 1000
```

### 4.2 Connection設定

```bash
# Azure OpenAI Connection作成
pf connection create \
  --file connections/azure_openai_connection.yaml \
  --name azure_openai_connection
```

```yaml
# connections/azure_openai_connection.yaml
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/AzureOpenAIConnection.schema.json
name: azure_openai_connection
type: azure_open_ai
api_key: ${env:AZURE_OPENAI_API_KEY}
api_base: ${env:AZURE_OPENAI_ENDPOINT}
api_type: azure
api_version: "2024-02-01"
```

### 4.3 Azure環境でのテスト

```bash
# Azure環境でFlow実行
pf run create \
  --flow estimation_agent \
  --data test_data.jsonl \
  --name test-run-001
```

### 4.4 Managed Online Endpoint デプロイ

```bash
# エンドポイント作成
az ml online-endpoint create \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace-name estimation-agent-workspace

# デプロイ
pf flow deploy \
  --flow estimation_agent \
  --endpoint estimation-agent-endpoint \
  --deployment-name blue \
  --instance-type Standard_DS3_v2 \
  --instance-count 1
```

### 実装タスク

- [ ] `generate_response.jinja2` 作成
- [ ] `flow.dag.yaml` 更新（LLMノード）
- [ ] Connection設定
- [ ] Azure環境でテスト実行
- [ ] Managed Online Endpoint デプロイ
- [ ] エンドポイント動作確認

---

## 🔄 Phase 5: CI/CD構築

**目的**: 自動テスト・自動デプロイの実現

### 5.1 GitHub Actions設定

```yaml
# .github/workflows/test.yml
name: Test Prompt Flow

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=estimation_agent
```

```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login (OIDC)
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Prompt Flow
        run: |
          pip install promptflow promptflow-tools
      
      - name: Deploy Flow
        run: |
          pf flow deploy \
            --flow estimation_agent \
            --endpoint estimation-agent-endpoint \
            --deployment-name blue
```

### 実装タスク

- [ ] `.github/workflows/test.yml` 作成
- [ ] `.github/workflows/deploy.yml` 作成
- [ ] Azure OIDC認証設定
- [ ] GitHub Secrets設定
- [ ] CI/CD動作確認

---

## 📋 calc API 仕様（決定事項）

> [!NOTE]
> Phase 1実装後、以下を決定してください

### 必要な決定事項

1. **エンドポイント**
   - URL: `https://????.azurewebsites.net/api/calculate`
   - メソッド: POST

2. **認証方法**
   - [ ] API Key（ヘッダー: `X-API-Key`）
   - [ ] Managed Identity
   - [ ] その他: ___________

3. **リクエスト形式**
```json
{
  "project_type": "web_app",
  "duration_months": 6,
  "team_size": 3
}
```

4. **レスポンス形式**
```json
{
  "total": 18000000,
  "breakdown": {
    "development": 12600000,
    "design": 3600000,
    "management": 1800000
  },
  "unit": "JPY"
}
```

5. **エラーレスポンス**
```json
{
  "error": true,
  "message": "エラーメッセージ",
  "code": "ERROR_CODE"
}
```

---

## 🎯 実装優先順位と次のステップ

### 今すぐ開始できること（Azure不要）

1. **Phase 0: 環境構築** 🔴 最優先
   - リポジトリ初期化
   - Prompt Flow インストール
   - ディレクトリ構造作成

2. **Phase 1: モック実装** 🔴 最優先
   - `flow.dag.yaml` 作成
   - `call_calc_tool.py`（モック版）
   - `generate_response_mock.py`
   - ローカル実行確認

3. **Phase 2: テスト** 🟡 高優先度
   - 単体テスト作成
   - Flow統合テスト

### Azure環境構築後に実施

4. **Phase 3: Azure環境** 🟢 中優先度
   - リソース作成
   - Azure OpenAI デプロイ

5. **Phase 4: Azure統合** 🟢 中優先度
   - LLMノード実装
   - エンドポイントデプロイ

6. **Phase 5: CI/CD** ⚪ 低優先度
   - GitHub Actions設定

---

## ✅ 設計原則チェックリスト（再確認）

| チェック項目 | Phase 1実装 | 備考 |
|------------|-----------|------|
| Agent がツール選択を決めている | ✅ | `flow.dag.yaml`で定義 |
| Agent がツール呼び出し順序を決めている | ✅ | DAGで `call_calc` → `generate_response` |
| UI は Agent に 1 回だけリクエストする | ✅ | （UI実装時に確認） |
| Tool 同士は通信していない | ✅ | `call_calc_tool.py` は独立 |
| Tool は Agent を知らない | ✅ | Tool は単純な関数 |
| エラー時の判断も Agent が行う | ✅ | `generate_response` でエラー処理 |
| **`aggregate_response.py` は不要** | ✅ | LLMノードで統合 |

---

## 📝 まとめ

### 重要な決定事項

1. **`aggregate_response.py` は実装しない**
   - 理由: Agent（LLM）の責務を分散させない
   - 代替: `generate_response` ノード（LLM）で統合

2. **段階的アプローチ**
   - Phase 0-2: Azureなしでローカル開発
   - Phase 3-5: Azure環境構築・統合

3. **モック実装の活用**
   - calc API仕様が未確定でも開発開始可能
   - 環境変数で本番/モック切り替え

### 次のアクション

**すぐに開始できること:**
1. Phase 0の環境構築
2. Phase 1のモック実装
3. Phase 2のテスト作成

**後で決定すること:**
1. calc API の詳細仕様
2. Azure リソース名
3. デプロイメント名
