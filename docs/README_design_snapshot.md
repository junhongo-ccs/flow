# プロジェクト現状把握スナップショット (2026-01-13時点)

> **注意**: 本ドキュメントは、実装を進めるための設計書・仕様書ではありません。あくまで第三者（およびAI）が現在のプロジェクト状態、構成、到達点を誤解なく把握するための「現状スナップショット」です。推測や将来の構想は含まず、**現在実装されている事実のみ** を記述しています。

## 1. プロジェクト概要

- **目的**: ユーザーの要望をチャット形式でヒアリングし、RAG（過去事例・知見）を活用して適切なシステム開発見積もり（工数・費用・スケジュール）を自動提示するシステムの構築。
- **現在の到達点**: 
  - UI から Azure AI Agent への疎通確認済み（チャット可能）。
  - Agent から RAG (Azure AI Search) への検索・参照確認済み。
  - **計算ロジック (Calc API) は実装済みだが、Agent からの統合呼び出しは未実装（接続待ち）の状態。**
- **対象範囲**:
  1.  **UI**: チャットインターフェース
  2.  **Agent**: 対話制御・RAG検索・Prompt Flow (Flask Wrapper)
  3.  **RAG**: ナレッジ検索 (Azure AI Search)
  4.  **Calc**: 見積もり計算ロジック (Azure Functions)

## 2. 全体構成

### コンポーネントと責務
| コンポーネント | 技術スタック | 責務 | 現状ステータス |
| :--- | :--- | :--- | :--- |
| **UI** | Vite (Vanilla JS), HTML/CSS | ユーザー入力の受付、チャット表示、API通信 | 実装済・稼働中 |
| **Agent** | Python (Flask), Azure OpenAI | 会話履歴管理、プロンプト構築、RAG検索、LLM対話 | 実装済・稼働中 (Calc呼び出し除く) |
| **RAG** | Azure AI Search | 過去の見積もり事例や設計指針の提供 | 実装済・連携確認済 |
| **Calc API** | Python (Azure Functions) | 画面数・機能に基づく厳密な工数・費用計算 | 実装済・単体稼働可 (Agent未接続) |

### 処理フロー (現状)
```ascii
[User]
  │ (1) Input Text / Select Option
  ▼
[UI (Browser)]
  │ (2) POST /score (JSON)
  ▼
[Agent (Flask App: app.py)] 
  │ (3) Lookup Knowledge
  │     ──> [RAG (Azure AI Search)]
  │     <── (Relevant Docs)
  │
  │ (4) (本来ここに Calc 呼び出しがあるが現在は未接続)
  │
  │ (5) Construct Prompt (Jinja2)
  │     (User Input + History + Knowledge)
  │
  │ (6) Call LLM
  │     ──> [Azure OpenAI (GPT-4o)]
  │     <── (Response Text)
  │
  │ (7) Extract Options / Formatter
  ▼
[UI (Browser)]
  │ (8) Render Message & Buttons
  ▼
[User]
```

## 3. リポジトリ構成

### 1. `junhongo-ccs/flow` (Agent)
Azure AI Agent のコアロジックおよび Prompt Flow 定義。現在は Flask アプリとしてホスティングされている。
- `estimation_agent/`
  - `app.py`: **[Entry Focus]** 現在のメインエントリポイント。Flask APIサーバー。
  - `flow.dag.yaml`: Prompt Flow 定義（Azure AI Foundry 用だが、`app.py` はこれを直接使わず独自のロジックで動作）。
  - `lookup_knowledge.py`: RAG (Azure AI Search) 検索ツール。
  - `generate_response.jinja2`: LLMプロンプトテンプレート。
  - **Notice**: `call_calc_tool.py` は `flow.dag.yaml` で定義されているが、ディレクトリ内に存在しない（テストコード `tests/` には痕跡あり）。

### 2. `junhongo-ccs/estimation-ui-app` (UI)
フロントエンドアプリケーション。
- `index.html`: エントリポイント。
- `app.js`: **[Entry Focus]** メインロジック。状態管理、DOM操作、API通信。
- `styles/`: デザインシステムおよびコンポーネントスタイル。

### 3. `junhongo-ccs/estimate-backend-calc` (Calc API)
見積もり計算特化のバックエンド。
- `function_app.py`: **[Entry Focus]** Azure Functions エントリポイント (`calculate_estimate`)。
- `estimate_config.yaml`: 単価・係数などの計算設定ファイル。

## 4. エントリポイントとI/O契約

### UI → Agent
- **URL**: `/score` (POST)
- **Input (Request)**:
  ```json
  {
    "user_input": {
      "message": "Webアプリを作りたい",
      "selected_option": "web_app"  // オプション (任意)
    },
    "session_id": "uuid-string",    // 継続会話用
    "conversation_history": []      // クライアント側履歴 (オプション)
  }
  ```

### Agent → UI
- **Output (Response)**:
  ```json
  {
    "message": "承知しました。ターゲットユーザーは？",
    "options": [                  // UIでボタン表示される選択肢
      {"label": "一般消費者", "value": "B2C"},
      {"label": "社内業務", "value": "internal"}
    ],
    "is_complete": false,         // 完了フラグ
    "markdown": null,             // 完了時に見積もりMDが入る
    "session_id": "uuid-string"
  }
  ```

### Agent → Calc API (未連携・仕様のみ)
- **URL**: `/api/calculate_estimate` (POST)
- **Input (想定)**:
  ```json
  {
    "screen_count": 10,
    "complexity": "medium",
    "features": ["auth", "payment"],
    "phase2_items": ["ia_design"],
    "phase3_items": ["ui_design"]
  }
  ```
- **Output (想定)**:
  - 概算費用 (`final_amount`)、内訳 (`breakdown`) を含む JSON。

## 5. 現在の実装状況

### ✅ できていること
1.  **UI - Agent 間の疎通**: まともに会話ができ、選択肢ボタンが表示される。
2.  **RAG 検索**: ユーザー入力に基づいて Azure AI Search からナレッジを取得し、プロンプトに注入できている。
3.  **LLM 回答生成**: Jinja2 テンプレートを使用し、ロールプレイ（コンサルタント）を行えている。
4.  **Calc API 単体**: Azure Functions として実装され、JSON を投げれば計算結果が返るロジックは存在する。

### ⚠️ 仮実装・未連携・課題
1.  **Agent と Calc の分断**: 
    - Agent (`app.py`) 内で Calc API を呼び出す処理が実装されていない。
    - Prompt Flow 定義 (`flow.dag.yaml`) には `call_calc` ノードがあるが、実ファイル `call_calc_tool.py` が `estimation_agent` フォルダに存在しない。
    - 結果として、現在の見積もり回答は LLM の推論のみ（またはハルシネーション）に頼っている可能性がある（正確な計算結果がプロンプトに入っていない）。
2.  **プロンプトへの計算結果注入**:
    - `generate_response.jinja2` テンプレート内に `{{ calc_result }}` のプレースホルダがなく、計算結果を受け取る口が用意されていない。

## 6. まとめ

現在は **「ガワ（UI + Agent会話）は動いているが、中身の計算エンジン（Calc）が脳（Agent）とつながっていない」** 状態です。
次のステップで、この「Agent → Calc API」の接続実装を行うことが、正確な見積もりシステム完成への最優先事項となります。
