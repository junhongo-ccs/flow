# RAG Implementation Overview

このドキュメントでは、`rags/` ディレクトリに配置されたドキュメントが、実際に RAG（Retrieval-Augmented Generation）として AI の回答生成に活用されるまでのプロセスを説明します。

## 全体プロセス

プロセスは大きく分けて以下の4つのステップで構成されています。

### 1. データの準備（Local Storage）
ナレッジとして活用したい情報を Markdown 形式で `estimation_agent/rags/` ディレクトリに保存します。
ここには以下の内容が含まれます：
- 料金表 (Price List)
- 過去のプロジェクト事例 (Case Studies)
- デザインガイドライン
- 開発プロセスや保守プランの仕様

### 2. インデックス登録（Indexing）
保存されたドキュメントを検索可能にするため、Azure AI Search に登録します。

- **実行スクリプト**: `estimation_agent/index_rags.py`
- **処理内容**: `rags/` 内のファイルを読み込み、Azure AI Search の `estimation-rags` インデックスにアップロードします。
- **特徴**: 日本語解析エンジン（`ja.microsoft`）を使用しているため、日本語での曖昧な検索にも対応しています。

### 3. プロンプトフローでの検索（Retrieval）
ユーザーから相談が来ると、Prompt Flow 内で関連情報を検索します。

- **実行ノード**: `lookup_knowledge`
- **ロジック**: `estimation_agent/lookup_knowledge.py`
- **処理内容**: ユーザーの入力内容を元に、Azure AI Search から関連度の高いドキュメントを上位3件（デフォルト）抽出します。
- **出力形式**: `--- Source: [ファイル名] ---\n[内容]` という形式で一つのテキストに統合されます。

### 4. LLM への注入（Feeding to LLM）
検索された知識が、最終的な回答生成に使用されます。

- **オーケストレーション**: `estimation_agent/flow.dag.yaml`
- **プロンプトテンプレート**: `estimation_agent/generate_response.jinja2`
- **処理内容**: 検索された `knowledge` がプロンプト内の `{{ knowledge }}` 部分に埋め込まれます。
- **効果**: LLM（GPT-4o）が「社内ドキュメント」としてこれらの情報を参照し、当社の基準や過去事例に基づいた具体的で根拠のある提案を生成します。

---

## 期待される効果
この RAG の仕組みにより、以下のメリットが得られます：
1. **正確な見積もり**: LLM の学習データに含まれない最新の独自の料金体系を反映可能。
2. **根拠の明示**: どの資料に基づいて回答したかを明示でき、ユーザーの信頼性を向上。
3. **個別の専門知識**: デザインやインフラなど、特定の分野に特化した詳細なナレッジを容易に追加・更新可能。
