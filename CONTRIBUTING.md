# 開発ガイド

このドキュメントは、開発チームがプロジェクトに参加する際のセットアップと開発フローを説明します。

---

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/junhongo-ccs/flow.git
cd flow
```

### 2. 仮想環境の作成

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
# 本番用依存関係
pip install -r requirements.txt

# 開発用依存関係（リンター、テストツール）
pip install -r requirements-dev.txt
```

---

## 📝 コーディング規約

### フォーマッター: Black

- **行長**: 100文字
- **ターゲット**: Python 3.8+

```bash
# コードをフォーマット
black .

# チェックのみ（変更しない）
black --check .
```

### リンター: Flake8

- **行長**: 100文字
- **無視するエラー**: E203, W503

```bash
# リントチェック
flake8 .
```

### 型チェッカー: mypy

- **Python バージョン**: 3.8

```bash
# 型チェック
mypy estimation_agent/
```

---

## 🧪 テスト

### テストの実行

```bash
# すべてのテストを実行
pytest tests/

# カバレッジ付きで実行
pytest --cov=estimation_agent --cov-report=html tests/

# 特定のテストファイルのみ
pytest tests/test_call_calc_tool.py
```

### テストカバレッジの確認

```bash
# HTMLレポートを生成
pytest --cov=estimation_agent --cov-report=html tests/

# ブラウザで確認
open htmlcov/index.html  # macOS
```

---

## 🔄 開発フロー

### 1. 新機能の開発

```bash
# 新しいブランチを作成
git checkout -b feature/your-feature-name

# コードを編集
# ...

# フォーマット
black .

# リントチェック
flake8 .

# 型チェック
mypy estimation_agent/

# テスト
pytest tests/

# コミット
git add .
git commit -m "Add your feature"

# プッシュ
git push origin feature/your-feature-name
```

### 2. コミット前のチェックリスト

- [ ] `black .` でフォーマット済み
- [ ] `flake8 .` でエラーなし
- [ ] `mypy estimation_agent/` でエラーなし
- [ ] `pytest tests/` ですべてのテスト成功
- [ ] 新機能にテストを追加

---

## 📚 ドキュメント

### 主要ドキュメント

- **API仕様書**: `docs/API_SPECIFICATION.md`
- **ユーザーマニュアル**: `docs/USER_MANUAL.md`
- **デプロイガイド**: `docs/manual_deployment_guide.md`
- **タスク管理**: `docs/task.md`

### Docstring スタイル

Google Style Docstringsを使用:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """関数の簡潔な説明。
    
    詳細な説明（必要な場合）。
    
    Args:
        arg1: 引数1の説明
        arg2: 引数2の説明
    
    Returns:
        戻り値の説明
    
    Raises:
        ValueError: エラーの説明
    """
    pass
```

---

## 🏗️ プロジェクト構造

```
flow/
├── estimation_agent/       # AI Agent本体
│   ├── app.py             # Flask wrapper
│   ├── call_calc_tool.py  # 計算API呼び出し
│   ├── lookup_knowledge.py # RAG検索
│   ├── upload_rags.py     # RAGアップロードスクリプト
│   └── rags/              # RAGドキュメント（23個）
├── tests/                 # テスト
├── docs/                  # ドキュメント
├── requirements.txt       # 本番用依存関係
├── requirements-dev.txt   # 開発用依存関係
├── pyproject.toml         # Black設定
├── .flake8                # Flake8設定
└── mypy.ini               # mypy設定
```

---

## 🔧 トラブルシューティング

### 仮想環境が有効化されない

```bash
# 仮想環境を削除して再作成
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Blackのフォーマットエラー

```bash
# 自動修正
black .

# 特定のファイルのみ
black estimation_agent/app.py
```

### mypyのエラー

```bash
# 型スタブをインストール
pip install types-requests types-PyYAML

# 特定のファイルのみチェック
mypy estimation_agent/app.py
```

---

## 📞 サポート

質問や問題がある場合は、GitHubのIssuesセクションを使用してください。

---

**最終更新**: 2025-12-30
