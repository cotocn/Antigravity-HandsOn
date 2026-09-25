# コーディングエージェント開発ガイド

## 前提条件

CLI ツールのインストール（初回のみ）:
```bash
uv tool install google-agents-cli
```

---

## 開発フェーズ

### フェーズ 1: 要件の把握
コードを書く前に、プロジェクトの要件、制約事項、成功基準を正しく理解してください。

### フェーズ 2: 実装とビルド
`app/` 配下にエージェントのロジックを実装します。対話的な動作確認には `agents-cli playground` を使用し、フィードバックに応じて改善します。

### フェーズ 3: 評価ループ（主要な改善フェーズ）
まず 1〜2 件の評価ケースから開始し、`agents-cli eval run` を実行して、満足いく品質になるまで修正と再実行を繰り返します。基準が整ったら、`agents-cli eval compare`（デグレ検知）、`agents-cli eval analyze`（失敗原因のクラスタリング）、`agents-cli eval optimize`（プロンプト自動最適化）を活用してください。

### フェーズ 4: デプロイ前テスト
`uv run pytest tests/unit tests/integration` を実行し、すべてのテストがパスするまで修正します。

### フェーズ 5: 開発環境へのデプロイ
**人間の明示的な承認が必要です。** ユーザーの確認を取った後でのみ `agents-cli deploy` を実行してください。

### フェーズ 6: 本番環境へのデプロイ
ユーザーに希望の構成を確認します: オプション A（シンプルな単一プロジェクト構成）または オプション B（`agents-cli infra cicd` による完全な CI/CD パイプライン構成）。

## 開発用コマンド一覧

| コマンド | 用途 |
|---|---|
| `agents-cli playground` | 対話的なローカル開発・動作確認環境の起動 |
| `uv run pytest tests/unit tests/integration` | 単体テストおよび統合テストの実行 |
| `agents-cli eval dataset synthesize` | マルチターン対話の評価シナリオを自動生成 |
| `agents-cli eval run` | 評価データセットを実行し、対話トレースを採点 |
| `agents-cli eval generate` / `agents-cli eval grade` | 分離実行: トレースの生成と採点を分けて実行 |
| `agents-cli eval compare` | 2 つの採点結果ファイルを比較（デグレ検知） |
| `agents-cli eval analyze` | 採点結果から失敗パターンを自動クラスタリング |
| `agents-cli eval metric list` | 利用可能な組み込み評価メトリクスの一覧表示 |
| `agents-cli eval optimize` | 評価データを用いてエージェントの指示文を自動最適化 |
| `agents-cli lint` | コード品質の静的チェック |
| `agents-cli infra single-project` | 単一プロジェクトのインフラ構築（Terraform） |
| `agents-cli deploy` | 開発環境へのデプロイ |
| `agents-cli scaffold enhance` | デプロイ先や CI/CD 設定をプロジェクトに追加 |
| `agents-cli scaffold upgrade` | プロジェクトを最新バージョンへ自動アップグレード |

---

## コーディングエージェントの行動指針

- **コードの保全**: ユーザーの要求に直接関係するコードのみを変更してください。周囲のコード、設定値（`model` など）、コメント、フォーマットは可能な限り保持してください。
- **モデルを勝手に変更しない**: 明示的な指示がない限り、指定された `model` を変更してはいけません。
- **モデルの 404 エラー**: モデル名ではなく `GOOGLE_CLOUD_LOCATION`（例: `us-east1` ではなく `global`）を修正してください。
- **ADK ツールのインポート**: モジュールではなくツールインスタンスをインポートしてください（例: `from google.adk.tools.load_web_page import load_web_page`）。
- **Python の実行は `uv` を使用**: `uv run python script.py` を使用します。事前に `agents-cli install` を実行してください。
- **同じエラーの繰り返しを防ぐ**: 同じエラーが 3 回以上続く場合は、闇雲に再試行せず根本原因を特定して修正してください。
- **Terraform の競合（Error 409）**: 再作成を繰り返すのではなく `terraform import` を使用してください。

---

## プロジェクト固有のルール

> 事業部記入欄

- なるべく早く作ってください。
- わからないことがあったら適当に補完して進めてください。
- 動けば OK です。
