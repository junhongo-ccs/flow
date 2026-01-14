# 技術スタック - AI見積もりシステム V2

**プロジェクト名**: AI見積もりシステム V2  
**バージョン**: 2.0  
**作成日**: 2025-12-30

## 1. アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (UI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Chat UI (HTML/CSS/JavaScript)                       │  │
│  │  - Message Timeline (AI/User Icons)                  │  │
│  │  - Option Buttons                                    │  │
│  │  - Free Text Input                                   │  │
│  │  - Session Reset (Restart button)                    │  │
│  │  - Markdown Download                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Azure AI Agent (Backend)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask App (app.py)                                  │  │
│  │  - /score endpoint                                   │  │
│  │  - Session Management                                │  │
│  │  - Conversation State                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│              ┌───────────────┼───────────────┐              │
│              ▼               ▼               ▼              │
│  ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐  │
│  │ Azure OpenAI    │ │ Azure AI    │ │ Prompt Template  │  │
│  │ (gpt-4o)        │ │ Search (RAG)│ │ (Jinja2)         │  │
│  │ - Chat          │ │ - 27 files  │ │ - Conversation   │  │
│  │ - Estimation    │ │ - Knowledge │ │ - Estimation     │  │
│  │ - Markdown Gen  │ │ - Pricing   │ │ - Schedule       │  │
│  └─────────────────┘ └─────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 2. フロントエンド技術スタック

### 2.1 コア技術
| 技術 | バージョン | 用途 |
|------|-----------|------|
| HTML5 | - | マークアップ |
| CSS3 | - | スタイリング |
| JavaScript (ES6+) | - | インタラクション |

### 2.2 スタイリング
- **Vanilla CSS**: カスタムデザインシステム
- **8pxグリッドシステム**: 既存のデザインシステムを継承
- **CSS Variables**: カラーパレット、スペーシング、タイポグラフィ
- **レスポンシブデザイン**: メディアクエリ

### 2.3 主要ライブラリ
- **なし**: 軽量化のため、外部ライブラリは使用しない
- **Fetch API**: バックエンドとの通信

### 2.4 ファイル構成
```
estimation-ui-app/
├── index.html              # チャットUI（フォーム削除）
├── app.js                  # チャットロジック
├── styles/
│   ├── design-system.css   # デザインシステム（既存）
│   └── app.css             # チャットUI用スタイル
└── README.md
```

## 3. バックエンド技術スタック

### 3.1 コア技術
| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.8+ | プログラミング言語 |
| Flask | 2.x | Webフレームワーク |
| Flask-CORS | - | CORS対応 |
| Azure OpenAI SDK | latest | GPT-4o連携 |
| Azure AI Search SDK | latest | RAG検索 |

### 3.2 Azure サービス
| サービス | 用途 |
|---------|------|
| Azure Container Apps | Flaskアプリのホスティング |
| Azure OpenAI Service | GPT-4o (チャット、見積もり生成) |
| Azure AI Search | RAG (23ナレッジファイル) |
| Azure AI Foundry | 統合管理 |

### 3.3 ファイル構成
```
flow/estimation_agent/
├── app.py                      # Flask アプリケーション
├── lookup_knowledge.py         # RAG検索ツール
├── call_calc_tool.py           # (V2では使用しない)
├── generate_response.jinja2    # プロンプトテンプレート
├── flow.dag.yaml               # Prompt Flow定義
├── requirements.txt            # Python依存関係
├── Dockerfile                  # コンテナイメージ
├── rags/                       # RAGナレッジベース
│   ├── 01_price_list_webapp.md
│   ├── 02_price_list_mobile.md
│   ├── ...
│   ├── 23_design_phase_checklist.md
│   ├── 24_project_schedules.md
│   ├── 25_schedule_case_studies.md
│   ├── 26_milestone_templates.md
│   └── 27_advanced_design_requirements.md  # (新規: 高度なデザイン要求)
└── deployment/
    ├── deployment.yaml
    └── endpoint.yaml
```

## 4. データフロー

### 4.1 会話フロー
```
1. ユーザー: チャットUIでメッセージ送信（選択肢 or 自由記述）
   ↓
2. Frontend: POST /score { user_input: {...}, conversation_history: [...] }
   ↓
3. Backend (Flask): リクエスト受信、セッション管理
   ↓
4. RAG検索: lookup_knowledge() - Azure AI Searchでナレッジ検索
   ↓
5. プロンプト生成: generate_response.jinja2 - 会話履歴 + RAG結果
   ↓
6. Azure OpenAI: GPT-4o で応答生成（次の質問 + 選択肢 or 最終見積もり）
   ↓
7. Backend: JSON応答 { message: "...", options: [...], is_complete: false }
   ↓
8. Frontend: AIメッセージ + 選択肢ボタンを表示
   ↓
9. 繰り返し（会話完了まで）
   ↓
10. 会話完了: is_complete: true, markdown: "..." 
   ↓
11. Frontend: Markdownダウンロードボタン表示
```

### 4.2 データ形式

#### リクエスト (Frontend → Backend)
```json
{
  "user_input": {
    "message": "Webアプリケーションの開発を検討しています",
    "selected_option": null
  },
  "conversation_history": [
    {
      "role": "user",
      "content": "見積もりをお願いします"
    },
    {
      "role": "assistant",
      "content": "どのようなシステムですか？",
      "options": ["Webアプリ", "モバイルアプリ", "両方", "その他"]
    }
  ],
  "session_id": "uuid-xxx"
}
```

#### レスポンス (Backend → Frontend)
```json
{
  "message": "Webアプリケーションですね。画面数はどのくらいを想定していますか？",
  "options": ["5-10画面", "10-20画面", "20画面以上", "その他"],
  "is_complete": false,
  "session_id": "uuid-xxx"
}
```

#### 最終レスポンス（会話完了時）
```json
{
  "message": "見積もりが完成しました。",
  "markdown": "# プロジェクト見積もり・提案書\n\n...",
  "is_complete": true,
  "session_id": "uuid-xxx"
}
```

## 5. RAG (Retrieval-Augmented Generation)

### 5.1 ナレッジファイル一覧 (27ファイル)
1. 料金表（Web/モバイル）
2. 開発プロセス
3. メンテナンスプラン
4. AI実装コスト
5. インフラコスト
6. 事例研究（EC/ポータル/マッチング）
7. 支払条件
8. 法的コンプライアンス
9. デザインコスト (SIer基準)
10. 支払条件
11. 法的コンプライアンス
12. テストサービス
13. データ移行
14. 多言語対応
15. API統合
16. 分析・レポート
17. トレーニング・サポート
18. ワイヤーフレームプロセス
19. デザイン会社協業
20. Figmaデザイン仕様
21. デザインから開発への引き継ぎ
22. デザインフェーズチェックリスト
23. プロジェクトスケジュール標準
24. スケジュール事例研究
25. マイルストーンテンプレート
26. 高度なデザイン要求事項 (デザインシステム等)
27. 開発チーム体制と役割 (※1-8, 05, 06も含む全27ファイル)

### 5.2 RAG検索戦略
- **セマンティック検索**: ユーザーの質問内容から関連ナレッジを検索
- **メタデータフィルタリング**: プロジェクトタイプ、フェーズなどでフィルタ
- **Top-K取得**: 関連度の高い上位3-5件を取得

## 6. プロンプトエンジニアリング

### 6.1 システムプロンプト
```
あなたは親切で知識豊富なシステム開発の見積もりアシスタントです。
クライアントとの会話を通じて、要件定義、デザインフェーズ、開発の
すべてのフェーズについてヒアリングし、詳細な見積もりとスケジュールを
提案します。

【重要な指示】
1. 一度に1つの質問をする（ユーザーを圧倒しない）
2. 必ずRAGの知識を参照して回答する
3. 適切な選択肢を3-4個提示する（常に「その他」を含める）
4. ユーザーの状況に応じて質問を調整する（柔軟性）
5. 会話が完了したら、Markdown形式の見積もり・提案書を生成する
```

### 6.2 見積もり生成プロンプト
```
RAGから取得した価格情報を基に、以下の構成で見積もりを計算してください：

【会話から収集した情報】
- プロジェクトタイプ: {{ project_type }}
- 画面数: {{ screen_count }}
- チームサイズ: {{ team_size }}
- 期間: {{ duration }}
- その他要件: {{ other_requirements }}

【RAGから参照した価格情報】
{{ rag_pricing_info }}

【計算方法】
1. 基本開発費 = RAGの料金表を参照
2. デザイン費 = 画面数 × デザイン単価（RAG参照）
3. インフラ費 = 要件に応じて（RAG参照）
4. その他 = 追加要件に応じて（RAG参照）

【アウトプット】
Markdown形式で詳細な見積もり書を生成
```

## 7. デプロイメント

### 7.1 フロントエンド
- **ホスティング**: Azure Static Web Apps (既存)
- **CI/CD**: GitHub Actions (既存)
- **URL**: https://[existing-frontend-url]

### 7.2 バックエンド
- **ホスティング**: Azure Container Apps (既存)
- **CI/CD**: GitHub Actions (既存)
- **エンドポイント**: https://estimation-agent-app.blueplant-e852c27d.eastus2.azurecontainerapps.io/score

### 7.3 環境変数
```bash
# Backend
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_ENDPOINT=xxx
AZURE_SEARCH_ENDPOINT=xxx
AZURE_SEARCH_KEY=xxx
USE_MOCK_CALC=false  # V2では使用しない
```

## 8. 開発環境

### 8.1 必要なツール
- **Git**: バージョン管理
- **Python 3.8+**: バックエンド開発
- **Node.js** (オプション): フロントエンド開発サーバー
- **Azure CLI**: Azureリソース管理
- **VS Code**: 推奨エディタ

### 8.2 ローカル開発
```bash
# Backend
cd flow/estimation_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend
cd estimation-ui-app
python -m http.server 8000
# または
npx serve .
```

## 9. テスト戦略

### 9.1 フロントエンド
- **手動テスト**: ブラウザでのUI/UX確認
- **レスポンシブテスト**: 各種デバイスサイズで確認

### 9.2 バックエンド
- **単体テスト**: RAG検索、プロンプト生成のテスト
- **統合テスト**: エンドツーエンドの会話フローテスト
- **RAGテスト**: 各ナレッジファイルが適切に検索されるか確認

## 10. パフォーマンス最適化

### 10.1 フロントエンド
- Vanilla JSで軽量化
- CSS最小化
- 画像なし（テキストベース）

### 10.2 バックエンド
- RAG検索のキャッシング（セッション内）
- プロンプトの最適化（トークン数削減）
- 非同期処理の活用

## 11. セキュリティ

### 11.1 フロントエンド
- XSS対策: ユーザー入力のエスケープ
- HTTPS通信のみ

### 11.2 バックエンド
- CORS設定の適切な管理
- APIキーの環境変数管理
- 入力バリデーション
- レート制限（将来対応）

## 12. モニタリング・ログ

- **Application Insights**: Azure標準のモニタリング
- **ログレベル**: INFO（本番）、DEBUG（開発）
- **メトリクス**: レスポンス時間、エラー率、RAG検索回数
