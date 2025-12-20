
---
# 📘 AI見積もりシステム - 全体仕様書（Azure OpenAI版・確定）

**バージョン**: 1.1.0  
**最終更新**: 2025-12  
**対象**: GitHub Copilot / Azure AI Agent / 開発者  
**目的**:  
Azure AI Agent を唯一の意思決定コアとし、  
Azure OpenAI を Agent 内推論に用いる見積もりシステムの全体像を定義する。

---

## 📑 目次

1. システム概要
    
2. アーキテクチャ
    
3. リポジトリ別役割定義
    
4. データフロー仕様
    
5. API仕様
    
6. 受け入れ条件
    
7. 非機能要件
    
8. 制約事項
    
9. 用語集
    

---

## 1. システム概要

### 1.1 目的

本システムは、  
**システム開発案件の見積もりを Azure AI Agent がオーケストレーションし、  
経営層が意思決定可能な根拠（HTML）を生成すること**を目的とする。

- 見積金額の算出は **AIを使用しない確定ロジック**
    
- 説明・根拠生成のみを **Azure OpenAI に限定**
    
- 判断・手順・統合は **すべて Agent が担う**
    

---

### 1.2 主要機能

|機能ID|機能名|説明|
|---|---|---|
|F-001|ユーザー入力収集|案件情報（画面数・複雑度等）を取得|
|F-002|基本金額計算|YAML設定に基づく非AI計算|
|F-003|根拠HTML生成|Azure OpenAI による説明文生成|
|F-004|統合レスポンス|金額・根拠・前提・注意事項を返却|

---

### 1.3 システム構成要素

```
┌────────────────────────────────────────────┐
│ estimation-ui-app（UI層）                  │
│ - 静的HTML / CSS / JS                      │
│ - Azure Static Web Apps                    │
└──────────────┬─────────────────────────────┘
               │ HTTPS POST
               ▼
┌────────────────────────────────────────────┐
│ Azure AI Agent（オーケストレーション層）   │
│ - Azure AI Foundry                         │
│ - Prompt Flow / Agent                     │
│ - Azure OpenAI（Agent内推論/生成）         │
│ - System Prompt で手順定義                 │
└──────────────┬─────────────────────────────┘
               │ Tool Call
               ▼
┌────────────────────────────────────────────┐
│ estimate-backend-calc（計算層）             │
│ - Azure Functions（Python）                │
│ - YAML係数設定                             │
│ - AI不使用                                │
└────────────────────────────────────────────┘
```

---

### 1.4 技術スタック

|層|技術|備考|
|---|---|---|
|UI|HTML / CSS / Vanilla JS|静的|
|Agent|Azure AI Foundry|Prompt Flow|
|**LLM**|**Azure OpenAI**|**Agent内でのみ使用**|
|計算API|Azure Functions (Python 3.11)|非AI|
|認証|Managed Identity / OIDC||
|デプロイ|SWA / Azure Functions||

---

## 2. アーキテクチャ

### 2.1 全体構成

```
User
 ↓
UI
 ↓（1回だけ）
Azure AI Agent
 ├─ Tool Call → calc API
 └─ Azure OpenAI（推論・生成）
 ↓
UI（表示のみ）
```

**重要**

- UIは Agent に **1回だけ** リクエスト
    
- Tool 同士の直接通信は禁止
    
- Agent が唯一の意思決定者
    

---

## 3. リポジトリ別役割定義

### 3.1 estimation-ui-app

**役割**: 入力と表示のみ  
**禁止**:

- 計算ロジック
    
- LLM呼び出し
    
- APIの順次制御
    

---

### 3.2 estimate-backend-calc

**役割**: 確定計算のみ（AI不使用）

- YAML設定に基づく計算
    
- Agent 以外の存在を知らない
    
- HTML生成禁止
    

---

### 3.3 Azure AI Agent

**プラットフォーム**: Azure AI Foundry  
**役割**: オーケストレーション

|項目|内容|
|---|---|
|LLM|Azure OpenAI|
|判断|Agent が実施|
|手順|System Prompt に明示|
|出力|HTML（doc--8px）|

---

### 3.3.1 利用する Azure OpenAI モデル（2025年12月時点）

Agent 内で利用可能・現実的な選択肢は以下：

|用途|推奨モデル|
|---|---|
|高品質な説明生成|**gpt-4o**|
|コスト重視 / PoC|**gpt-4o-mini**|
|安定性重視|**gpt-4.1 系列（提供地域次第）**|

※ **Agentの外から直接呼ばない**  
※ モデル選択は Agent 設定で切替可能

---

### 3.3.2 Prompt Flow 構成

```
flows/estimation_agent/
├── flow.dag.yaml
├── call_calc_tool.py
├── generate_rationale.jinja2
├── system_prompt.txt
```

---

### 3.3.3 プロンプト（Azure OpenAI前提）

- Gemini という単語は **一切使用しない**
    
- 「Azure OpenAI による推論・生成」と明記
    
- エラー文言も **Azure OpenAI エラー** に統一
    

---

## 4. データフロー仕様

### 正常系

```
UI → Agent
Agent → calc API
Agent → Azure OpenAI
Agent → UI
```

### エラー系

- calc エラー → Agent が説明HTML生成
    
- Azure OpenAI エラー → Agent がフォールバックHTML生成
    

---

## 5. API仕様

### 5.1 Agent API

- UI が呼ぶ唯一の API
    
- 内部で Tool / LLM を切替
    

---

## 6. 受け入れ条件（抜粋）

- UI → Agent 呼び出しは1回のみ
    
- 金額は calc API 結果と完全一致
    
- HTMLは `<div class="doc--8px">` 必須
    
- LLMは Azure OpenAI のみ
    

---

## 7. 非機能要件

|項目|要件|
|---|---|
|Agent P99|< 5秒|
|calc P99|< 500ms|
|可用性|99.9%|
|拡張性|Tool追加は Agent のみ変更|

---

## 8. 制約事項

- **LLMは Agent 内でのみ使用**
    
- UI / API から Azure OpenAI を直接呼ばない
    
- 判断ロジックはコードに書かない
    

---

## 9. 用語集（更新）

|用語|定義|
|---|---|
|Azure AI Agent|唯一の意思決定・統合主体|
|Azure OpenAI|Agent 内推論・生成用 LLM|
|Tool Call|Agent → 外部API 呼び出し|

---

## 📄 配置先（確定）

```
estimation-ui-app/docs/00_system_specification.md
estimate-backend-calc/docs/00_system_specification.md
flows/estimation_agent/docs/00_system_specification.md
```

---

## ✅ 状態まとめ

- ✅ Gemini 完全排除
    
- ✅ Azure OpenAI に一本化
    
- ✅ Agent 中心設計を厳密に維持
    
- ✅ 憶測なし・整合済み
    

---

次に進むなら、選択肢は **2つだけ** です：

1. **East US で Azure AI Foundry + Agent を作る具体手順**
    
2. **「この設計を壊さない」最小構成の Prompt Flow 実装**
    

どちらから行きますか。