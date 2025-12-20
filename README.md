# Estimate Agent Flows

Azure AI Agent / Prompt Flow を使用した見積もりロジックのオーケストレーション。

## 🚀 はじめに

このプロジェクトは、Azure AI Foundry (Prompt Flow) を使用して、見積もり計算 API (`calc API`) と LLM を連携させ、ユーザーに対して最適な見積もり回答を提供するエージェントを構築します。

### 前提条件

- Python 3.11+
- `pip install promptflow promptflow-tools promptflow-devkit`

### 環境構築

```bash
cd estimation_agent
pip install -r requirements.txt
cp .env.example .env
# .env を編集
```

### ローカル実行

```bash
pf flow test --flow estimation_agent --inputs user_input='{"project_type":"web_app","duration_months":6,"team_size":3}'
```

## 📂 ディレクトリ構造

- `estimation_agent/`: Prompt Flow 本体
- `tests/`: 統合テスト / 単体テスト
- `docs/`: 設計書・実装プラン

## 📜 設計原則

本プロジェクトは **Agent中心設計** を厳守します。詳細は `docs/00_design_principles.md` を参照してください。

## 🛠 開発フェーズ

現在は **Phase 1: Prompt Flow基本実装（モック版）** に向けて環境構築中です。
詳細は `docs/flows_implementation_plan.md` を参照してください。
