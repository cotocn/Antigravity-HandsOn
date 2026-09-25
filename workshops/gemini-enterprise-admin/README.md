# Gemini Enterprise 管理者向け Antigravity ハンズオン

Gemini Enterprise 管理者を対象にした 3 時間のワークショップ教材です。
受講者は各自のローカル PC 上の **Antigravity 2.0** から、Antigravity と対話しながら
エージェントの**開発規約を定め、生成させ、審査し、全社公開する**までを体験します。

📄 **設計書（正本）**: [Google Docs](https://docs.google.com/document/d/1j0rVQYcEe66Qm3IFMxkFXi3OvW7_e7CFgw3eWzMHsvE/edit) / [docs/workshop-guide.md](docs/workshop-guide.md)

## 前提：2 つの層を混同しないこと

| | 開発時ハーネス | 実行時エージェント |
|---|---|---|
| 成果物 | `AGENTS.md` / `skills/*/SKILL.md` | `agent.py` の `instruction=` |
| 読み手 | **Antigravity**（コーディングエージェント） | デプロイされた ADK エージェント |
| デプロイ | **されない** | される |
| 誰が書くか | **受講者（管理者）** | **Antigravity が生成する** |

> [!IMPORTANT]
> `SKILL.md` は Antigravity を動かすためのものであり、エージェント本体の中身ではありません。
> 本ワークショップの因果は **「規約を書く → Antigravity が生成する → 品質が変わる」** という間接的なものです。

## 学習の流れ

```
[配布] 事業部から申請された低品質なエージェント（API キー直書き、instruction が 1 文だけ）
   │
   ① AGENTS.md を「全社エージェント開発規約」に書き換える       ← 受講者が書く
   ② /masakari スキル（辛口レビュー）を作成する                  ← 受講者が書く
   ③ hooks.json を作成し、ガードレールを設定する                  ← 受講者が書く
       ├─→ PreToolUse: 危険コマンド（rm -rf 等）を物理遮断
       └─→ Stop: ソースコード内のシークレット直書きを検知し完了を拒否
   ④ エージェントを見直させる（★本日の山場）                      ← Antigravity が修正
       ├─→ エージェントが完了しようとする → Stop フックが発火して完了拒否
       ├─→ ガードレールの指摘（環境変数から読め）を受け、エージェントが自己修正
       └─→ --no-wait で Agent Runtime への配備を先行起動（＝技術的配備）
   ⑤ agents-cli eval run で受入評価 → 公開可否を判断（承認ゲート）
   ⑥ 配備確認（deploy --status）→ Gemini Enterprise に登録 ＝ 全社公開
```

> [!TIP]
> **デプロイ（技術的配備）と公開（承認を伴う管理判断）は別物です。**
> ④ の直後に配備を始め、⑤ の評価結果を確認してから ⑥ で全社公開します。

> [!IMPORTANT]
> **お願いと、強制は違います。**
> 規約（AGENTS.md）やレビュー（Skill）だけでは、エージェントが規約を無視するのを防げません。
> 物理的に「終了させない」Hook の門番が効く瞬間を体感することが本ワークショップの最大の学びです。

## タイムテーブル（概要）

| 時間 | パート | 内容 |
| --- | --- | --- |
| 70 分 | 第 1 部 座学 | エージェントの進化 / ハーネス工学（AGENTS.md・SKILL.md・Hooks・MCP）/ ガバナンス基礎 |
| 10 分 | 休憩 | 環境の最終疎通確認 |
| 80 分 | 第 2 部 ハンズオン | ①〜⑥ |
| 20 分 | 第 3 部 | 高度ガバナンス（Model Armor / Agent Gateway / IAM）・FinOps・ラップアップ |

## ディレクトリ構成

| パス | 配布 | 内容 |
| --- | --- | --- |
| [`docs/workshop-guide.md`](docs/workshop-guide.md) | 講師 | ワークショップ設計書（本体） |
| [`docs/prerequisites.md`](docs/prerequisites.md) | 受講者 | 事前準備チェックリスト（PC 環境 / API / IAM / GE App） |
| [`starter-kit/`](starter-kit/) | 受講者 | 配布用一式（API キー直書きエージェント、未設定の hooks.json） |
| [`answers/`](answers/) | 講師のみ | 模範解答。脱落者救済用 |
| [`governance/`](governance/) | 講師 | Model Armor / Agent Gateway の設定サンプル（第 3 部で解説） |

### starter-kit の中身

| ファイル | 層 | 状態 |
| --- | --- | --- |
| `AGENTS.md` | 開発時 | ⚠️ 事業部が書いた緩い 3 行。① で全社規約に書き換える |
| `app/agent.py` | 実行時 | ⚠️ `MARKETING_API_KEY` 直書き、`instruction` が 1 文。**手で編集せず、エージェントに直させる** |
| `.agents/scripts/validate_tool_call.py` | 開発時 | ✅ 危険コマンド遮断スクリプト（講師提供） |
| `.agents/scripts/scan_secrets.py` | 開発時 | ✅ シークレット直書き検知スクリプト（講師提供） |
| `.agents/hooks.json` | 開発時 | ❌ 意図的に未作成。③ で受講者が作成する |
| `tests/eval/datasets/ecommerce-eval.json` | — | ✅ EC 売上データ分析用の評価ケース（カテゴリ集計、存在しない商品ID、範囲外対応） |
| `tests/eval/eval_config.yaml` | — | ✅ LLM-as-judge メトリクス設定 |

> [!WARNING]
> `answers/` を受講者に事前共有しないでください。演習が成立しなくなります。

## 事前準備

受講者は開催前までに [`docs/prerequisites.md`](docs/prerequisites.md) をすべて完了させてください。

- ローカル PC への Antigravity 2.0 / `uv` / `gcloud` のインストール
- `uv tool install google-agents-cli`
- 必須 API の有効化（`aiplatform` / `cloudbuild` / `artifactregistry` / `discoveryengine`）
- IAM ロールの付与
- Gemini Enterprise アプリの事前作成

## 受講者の始め方

```bash
cp -r workshops/gemini-enterprise-admin/starter-kit ~/ge-workshop
cd ~/ge-workshop
uv sync

# Antigravity でワークスペースを開いてハンズオン開始
```
