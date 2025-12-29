# ドキュメント構成

このディレクトリには、AI見積もりシステムの各種ドキュメントが格納されています。

---

## 📁 ディレクトリ構成

### 📋 現在のドキュメント

#### `/` (ルート)
- **task.md** - プロジェクトのタスク管理（v1.0 - 現行システム）

#### `/specifications` (仕様書)
- **00_system_specification.md** - システム仕様書
- **API_SPECIFICATION.md** - API仕様書

#### `/guides` (ガイド・マニュアル)
- **USER_MANUAL.md** - ユーザーマニュアル（営業向け）

#### `/deployment` (デプロイ関連)
- **manual_deployment_guide.md** - 手動デプロイガイド
- **AZURE_OIDC_SETUP.md** - Azure OIDC設定ガイド
- **GITHUB_SECRETS.md** - GitHub Secrets設定ガイド

#### `/archive` (アーカイブ)
- **00_design_principles.md** - 設計原則（初期版）
- **flows_implementation_plan.md** - 実装計画（初期版）
- **implementation_plan.md** - 実装計画（古いバージョン）
- **deployment_status_report.md** - デプロイ状況レポート（古い）
- **project_status_report_executive_summary.md** - プロジェクト状況サマリー
- **project_status_report_technical_memo.md** - 技術メモ

---

## 🔍 用途別ドキュメント一覧

### システムを理解したい
1. `specifications/00_system_specification.md` - システム全体の仕様
2. `specifications/API_SPECIFICATION.md` - API仕様
3. `archive/00_design_principles.md` - 設計思想

### システムを使いたい
1. `guides/USER_MANUAL.md` - ユーザーマニュアル
2. `specifications/API_SPECIFICATION.md` - API仕様

### デプロイしたい
1. `deployment/manual_deployment_guide.md` - デプロイ手順
2. `deployment/AZURE_OIDC_SETUP.md` - Azure設定
3. `deployment/GITHUB_SECRETS.md` - GitHub設定

### 開発に参加したい
1. `../CONTRIBUTING.md` - 開発ガイド
2. `task.md` - 現在のタスク
3. `specifications/00_system_specification.md` - システム仕様

### 過去の経緯を知りたい
1. `archive/` - 過去のドキュメント

---

## 📝 次期バージョン（v2.0 - チャットボット版）

次期バージョンの計画は、artifactsディレクトリに格納されています：
- `/Users/hongoujun/.gemini/antigravity/brain/.../implementation_plan.md`
- `/Users/hongoujun/.gemini/antigravity/brain/.../task_v2_chat.md`

---

**最終更新**: 2025-12-30
