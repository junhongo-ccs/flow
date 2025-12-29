
---# 🎯 設計原則宣言（Agent中心設計・確定版）

**このドキュメントは、すべての設計・実装の前に必ず確認する不変条件です。**  
本プロジェクトでは **Azure AI Agent が唯一の意思決定コア** であり、他のすべてのコンポーネントは Agent によってオーケストレーションされます。

---

## 📜 不変条件（Invariant Principles）

### 1. Azure AI Agent が唯一の意思決定者である

- ✅ **Agent が**「何を計算するか」「どのツールを呼ぶか」「どの順序で実行するか」「結果をどう統合するか」を決定する

- ❌ UI / API / Functions が判断ロジックを持ってはならない

- ❌ UI や API が手続き的に処理順序を制御してはならない

---

### 2. UI / API / Functions はすべて Agent の Tool である

- ✅ 各コンポーネントは **受動的** な存在（呼ばれたら応答するだけ）

- ✅ Tool は Agent に登録され、Agent からのみ呼ばれる

- ❌ Tool 同士が直接通信してはならない

- ❌ Tool が Agent の存在を意識してはならない

---

### 3. 手続き的フローは Agent 内に閉じ込める

- ✅ 手順は **System Prompt / Prompt Flow** に記述する

- ✅ 依存関係・順序は Prompt Flow で表現する

- ❌ UI の JavaScript で `calc → enhance → agent` のような順次制御は禁止

- ❌ API が別の API を呼ぶ実装は禁止

---

## ✅ 正しいアーキテクチャ（Agent中心・修正版）

> **重要**
>
> - Agent は 1 つの箱で表現する（統合判断まで含めて Agent の責務）
>
> - Tool Call は _並列も可能_ だが、通常は **依存関係により順序制御** される
>

```
┌─────────┐
│   UI    │ ← 入力と表示のみ
└────┬────┘
     │ ① userInput
     ▼
┌──────────────────────────────────────┐
│        Azure AI Agent                 │
│  (Prompt Flow / System Prompt)        │
│                                      │
│  ② Tool Call: calc API                │
│        ↓                              │
│     calc_result                       │
│                                      │
│  ③ Tool Call: enhance / 補足 (任意)   │
│        ↓                              │
│     enhance_result                    │
│                                      │
│  ④ 結果を統合・判断                   │
│     finalResponse 生成                │
└───────────────┬──────────────────────┘
                │ ⑤ finalResponse
                ▼
           ┌─────────┐
           │   UI    │ ← 表示だけ
           └─────────┘
```

---

## 🔍 なぜこの図が「正しい」のか

### (A) Agent は 1 つで完結している

- Tool の呼び出し

- 結果の受領

- 成功 / 失敗の判断

- 最終レスポンス生成

👉 **すべて Agent の内部責務**  
👉 「Agent（統合判断）」という別箱は不要

---

### (B) 手順は Agent が管理している

- calc → enhance → 統合 の順序は **Prompt Flow / System Prompt** に記述

- UI はその順序を一切知らない

👉 UI が賢くならない = 設計が壊れない

---

## 🚦 Agent 的か？チェックリスト（必須）

設計・実装・レビュー前に必ず確認すること。

|チェック項目|Yes / No|
|---|---|
|Agent がツール選択を決めている|□|
|Agent がツール呼び出し順序を決めている|□|
|UI は Agent に 1 回だけリクエストする|□|
|Tool 同士は通信していない|□|
|Tool は Agent を知らない|□|
|エラー時の判断も Agent が行う|□|

※ 1 つでも No があれば **設計やり直し**

---

## ❌ よくあるアンチパターン

### UI が手順を制御している

```javascript
// ❌ NG
const calc = await fetch(calcAPI)
const enhance = await fetch(enhanceAPI, calc)
const result = await fetch(agentAPI, enhance)
```

👉 UI が意思決定者になっている

---

### API が別の API を呼んでいる

```python
# ❌ NG
result = calculate()
return requests.post("/enhance", result)
```

👉 Tool が Tool を呼んでいる

---

## ✅ 正解パターン（最小）

```javascript
// ✅ OK
const result = await fetch(agentEndpoint, { userInput })
display(result)
```

---

## 📌 このドキュメントの配置場所（必須）

```
estimation-ui-app/docs/00_design_principles.md
estimate-backend-calc/docs/00_design_principles.md
flows/estimation_agent/docs/00_design_principles.md
```

**すべての設計レビュー・PR レビューで本ドキュメントを基準に判断すること。**

---

## 🧠 最後に

> Agent が賢いのではない。  
> **設計が Agent を賢くしている。**

この原則を破らない限り、

- モデルが変わっても

- Azure の UI が変わっても

- Tool が増えても

**システムは壊れません。**
**すべての設計レビュー・PR レビューでこのドキュメントを参照すること。**
