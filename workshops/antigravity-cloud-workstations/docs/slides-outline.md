# Antigravity 実践ワークショップ：エージェント型AI開発と仕様駆動開発 (SDD)
## 社外受講者向け研修カリキュラム・スライド構成設計書（座学＋ハンズオン）

---

## 1. 研修の全体像と狙い

### 対象受講者
- エンタープライズ企業のアーキテクト、リードエンジニア、開発者、プラットフォーム推進担当者
- 「AIコード補完から、AIエージェントによる自律開発・システムモダナイゼーションへのシフト」を目指す技術者

### 研修の目標 (Learning Objectives)
1. **エージェント型開発パラダイムの理解**: 単なるコード自動生成と、エージェント型自律開発（ハーネス構造、ライフサイクル）の質的な違いを理解する。
2. **ハーネス（Harness）設計とガバナンス**: Rules, Skills, Hooks, MCP, Subagents の 5大要素を体系的に理解し、AIの暴走を防ぐ確定的ガードレールとチーム開発規約を設計できる。
3. **仕様駆動開発 (SDD: Spec-Driven Development)**: Explore → Plan → Code → Deliver の 4段階サイクルにより、テストや受け入れ基準を「正解仕様」として渡す確実な開発プロセスを体得する。
4. **Cloud Workstations × Antigravity 実践ハンズオン**: ゼロトラストでセキュアな開発環境（Cloud Workstations）上で、Antigravity（Code OSS / CLI）を操作し、実案件レベルのリファクタリング・モダナイゼーションとテスト駆動検証を完遂する。

---

## 2. カリキュラム構成（タイムテーブル案：半日 4時間コース）

| 時間 | セクション | 形式 | 主な内容 |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:30 (30m)** | **Chapter 1: エージェント型AI開発のパラダイムシフト** | 座学 | ・自動補完（Copilot型）から自律型エージェント（Antigravity型）へ<br>・モデル能力依存から「ハーネス工学（Context & Harness Engineering）」へ<br>・コンテキスト管理とトークン最適化（プロンプトキャッシュ） |
| **00:30 - 01:15 (45m)** | **Chapter 2: Antigravity ハーネス構造の完全理解** | 座学＋ミニ体験 | ・5大要素: Rules, Skills, Hooks, MCP, Subagents<br>・Rules (AGENTS.md) によるチーム規約と一次情報検証<br>・Skills によるオンデマンド手順書（Progressive Disclosure）<br>・Hooks による決定論的ガードレールと事前・事後自動化<br>・MCP (Model Context Protocol) と Google Cloud MCP エコシステム |
| **01:15 - 01:45 (30m)** | **Chapter 3: 仕様駆動開発 (SDD) 実践論** | 座学 | ・なぜプロンプト一発生成は破綻するのか？<br>・4段階サイクル: Explore（現状調査）→ Plan（正解仕様定義）→ Code（実装）→ Deliver（検証）<br>・2-Fix ルール（修正が2回失敗したらコンテキストを切り戻す原則）<br>・批判的レビュー（/masakari）による仕様のブラッシュアップ |
| **01:45 - 02:00 (15m)** | **休憩 (Break)** | - | - |
| **02:00 - 03:30 (90m)** | **Chapter 4: 実践ハンズオン Lab (Cloud Workstations)** | ハンズオン | **Lab: Web アプリケーションのマイクロサービス化＆高可用性リファクタリング**<br>・Step 0: Cloud Workstations ログイン & Antigravity 起動<br>・Step 1: ワークスペースハーネスの設定 (AGENTS.md / Hooks)<br>・Step 2: SDD サイクルによる既存コードの Explore と設計仕様策定<br>・Step 3: Antigravity によるコードリファクタリング & IaC 作成<br>・Step 4: テスト駆動検証 (Deliver) とクリーンアップ |
| **03:30 - 04:00 (30m)** | **Chapter 5: エンタープライズ導入・ガバナンス・FinOps & まとめ** | 座学＋Q&A | ・セキュリティ・コンプライアンス（VPC-SC、Cloud Audit Logs、IAM）<br>・FinOps: コンテキストバジェット管理とトークンコスト最適化<br>・Wrap-up & 質疑応答 |

---

## 3. スライド詳細構成案（全 30〜35 枚）

### 【Part 1: 基礎・座学編】

#### Chapter 1: エージェント型AI開発のパラダイムシフト
- **Slide 1: タイトルスライド**
  - タイトル: Google Antigravity 実践ワークショップ
  - サブタイトル: エージェント型AIハーネス設計と仕様駆動開発 (SDD) によるクラウドモダナイゼーション
- **Slide 2: 本研修のゴールとアジェンダ**
  - 今日の達成目標（ハーネス理解、SDD実践、セキュア環境でのハンズオン）
- **Slide 3: 生成AI開発の進化：自動補完から自律型エージェントへ**
  - 第一世代: インライン自動補完（行単位、受動的）
  - 第二世代: チャットボット（単一ターンの質疑応答）
  - 第三世代: **自律型エージェント (Antigravity)**（複数ターン、ファイル探索、コマンド実行、自己修復、計画実行）
- **Slide 4: モデル中心主義から「ハーネス工学」へ**
  - 「賢いLLM」だけでは業務開発は成功しない。
  - ハーネス（Harness）＝ モデルを取り囲むプロンプト設計、権限統制、ツール群、フィードバックループの総体。
  - 差がつくのはモデルの性能ではなく、ハーネスの品質。
- **Slide 5: コンテキスト管理とトークン経済性 (FinOps)**
  - コンテキストウィンドウの罠: 詰め込みすぎによる「コンテキスト劣化 (Attention Drift)」
  - 暗黙的プロンプトキャッシュの活用（最大 90% のコスト削減とレイテンシ短縮）
  - タスクごとのリフレッシュ（`/clear`）とスコープ限定。

#### Chapter 2: Antigravity ハーネスの 5 大要素
- **Slide 6: Antigravity ハーネスの全体アーキテクチャ**
  - 5 つの構成要素の概念図:
    1. **Rules (AGENTS.md)**: 常時適用される憲法・規約
    2. **Skills (SKILL.md)**: 必要な時にだけ読み込まれる業務手順書 (Progressive Disclosure)
    3. **Hooks (hooks.json)**: 実行前後に確定的・自動的に割り込むインターセプター
    4. **MCP (Model Context Protocol)**: 外部データ・API連携
    5. **Subagents**: 専門タスクの並行・階層委託
- **Slide 7: Rules (AGENTS.md) — チームの憲法を定義する**
  - なぜ必要か: 推測（ハルシネーション）の抑止、命名規則、Gitコミット規約、テスト強制。
  - ベストプラクティス: 「一次情報検証 (First-Party Verification)」の義務化。
- **Slide 8: Skills (SKILL.md) — 段階的開示によるスマートな手順書**
  - なぜ全てを AGENTS.md に書かないのか？（コンテキスト枯渇の防止）
  - Progressive Disclosure: 必要になった時だけファイルを参照する仕組み。
  - スラッシュコマンド連携と自然言語トリガー。
- **Slide 9: Hooks (hooks.json) — 決定論的ガードレール**
  - LLM の推論に頼らない、確実なルール強制（Pre-Invocation / Post-Invocation）。
  - 例1: 曖昧なプロンプトに対して自動で問い直しを行う「auto-grill-me」。
  - 例2: コマンド実行前の危険操作ブロック（rm -rf 等の静的チェック）。
- **Slide 10: MCP (Model Context Protocol) と Google Cloud エコシステム**
  - MCP の基本: LLM と外部システムを標準インターフェースで接続。
  - Google マネージド MCP サーバー群（BigQuery、Cloud Storage、AlloyDB、Monitoring 等）。
  - Dual-Layer セキュリティ: IAM 認証＋個別 API 権限による厳格な認可。
- **Slide 11: Subagents — 責務の分離と並行処理**
  - 1つのセッションに全てを背負わせない。
  - リサーチ専用エージェント、コード生成エージェント、レビュー専用エージェントの分業。

#### Chapter 3: 仕様駆動開発 (SDD: Spec-Driven Development)
- **Slide 12: なぜプロンプト一発でコードを書かせてはいけないのか？**
  - 失敗パターン: いきなり「○○なシステム作って」→ 見た目は動くがテスト不能・SPOFだらけのスパゲッティコード。
  - エージェントは「正解の基準」がなければ自律検証できない。
- **Slide 13: SDD 4 段階サイクル (Explore → Plan → Code → Deliver)**
  - 1. **Explore (調査)**: 編集禁止。既存コード・仕様・依存関係の可視化。
  - 2. **Plan (仕様・受入れ基準の策定)**: 何をもって完成とするか？（テスト要件、SLA、API仕様）。
  - 3. **Code (実装)**: Plan で合意した仕様に沿って最小限の差分で実装。
  - 4. **Deliver (確定的検証)**: テスト自動実行、ビルド、静的解析。100% 合格するまで自己修復。
- **Slide 14: 2-Fix ルール（暴走防止の鉄則）**
  - エージェントが修正を 2 回連続で失敗した場合、3 回目を試させてはならない。
  - 原因: コンテキストに過去のエラーログが蓄積し、モデルの推論が混乱している。
  - 対処: 直ちにロールバックし、プロンプトまたは Plan（仕様）を見直して新規セッションでやり直す。
- **Slide 15: 批判的レビュー（Critique / Masakari）**
  - 実装前に「Socratic な問いかけ」を行い、設計の抜け漏れや非機能要件の欠陥を炙り出す。

---

### 【Part 2: ハンズオン実践編】

#### Chapter 4: 実践ハンズオン Lab
- **Slide 16: ハンズオンの目的とシナリオ**
  - シナリオ: 単一リージョンで動作する既存 Web アプリケーション（Monolith / 単一障害点あり）を、高可用性・マルチリージョン構成にモダナイズする。
  - 使用環境: **Google Cloud Workstations**（ブラウザから即座にアクセス可能なセキュア開発コンテナ）。
- **Slide 17: Cloud Workstations × Antigravity 開発環境の特長**
  - ローカル端末へのソースコード持ち出しゼロ（データ漏洩防止）。
  - Antigravity CLI (`agy`) および Code OSS（ブラウザ版 VS Code）が事前セットアップ済み。
  - VPC 内部で安全に実行される開発インフラ。
- **Slide 18: Lab Step 0: 環境接続と確認**
  - Cloud Workstations へのアクセス手順。
  - ターミナルでの `agy --version` 確認。
  - 演習リポジトリの clone と初期動作確認。
- **Slide 19: Lab Step 1: ワークスペースハーネスの構成**
  - 演習ディレクトリ直下に `AGENTS.md` を配置。
  - 「First-Party Verification」「テスト先行」「2-Fix ルール」の規約を定義。
- **Slide 20: Lab Step 2: SDD サイクル ① - Explore (現状分析)**
  - プロンプト指示: 「コードを一切変更せず、既存の構成の単一障害点 (SPOF) と非機能要件のボトルネックを洗い出し、`baseline_summary.md` にまとめよ」
  - Antigravity の自律探索を体験。
- **Slide 21: Lab Step 3: SDD サイクル ② - Plan (モダナイゼーション計画)**
  - プロンプト指示: 「Cloud Run + AlloyDB 高可用性構成へ移行するための仕様書 `plan.md` を作成せよ。受け入れテスト条件を明記すること」
  - 仕様レビューとブラッシュアップ。
- **Slide 22: Lab Step 4: SDD サイクル ③ - Code (実装・リファクタリング)**
  - プロンプト指示: 「`plan.md` に基づき、必要なコンポーネントを段階的に実装せよ」
  - 差分確認とコミットの分離。
- **Slide 23: Lab Step 5: SDD サイクル ④ - Deliver (テストと検証)**
  - 自動テストスクリプトの実行。
  - エラー発生時のエージェントによる自己診断・自己修復の観察。
- **Slide 24: Lab Step 6: 振り返りとクリーンアップ**
  - 成果物の確認（アーキテクチャ図、差分、テスト結果）。
  - 演習リソースの確実な解放と後片付け。

---

### 【Part 3: ガバナンス・運用・エンタープライズ展開】

#### Chapter 5: エンタープライズ導入・ガバナンス・FinOps
- **Slide 25: エンタープライズ AI 開発の 4 層セキュリティモデル**
  - 1. **インフラセキュリティ**: Cloud Workstations + VPC Service Controls によるデータ境界保護。
  - 2. **認証・認可**: Workload Identity、IAM Deny による本番アクセス保護。
  - 3. **ハーネスガードレール**: Hooks による危険コマンドの事前ブロック。
  - 4. **監査証跡**: Cloud Audit Logs による全プロンプト・ツール呼び出しログの保存。
- **Slide 26: 開発組織への展開パターン（チームハーネスの標準化）**
  - リポジトリ共有型の `AGENTS.md` とチーム標準 Skills の配布。
  - CI/CD パイプラインへのエージェント評価（Evals）の組み込み。
- **Slide 27: まとめ — エージェントを最高のペアプログラマーにするために**
  - 1. コンテキストを絞り込む（不要な情報は食わせない）
  - 2. 仕様（テスト・合格基準）を先に定義する（SDD の徹底）
  - 3. 確定的ガードレール（Hooks・Rules）で囲う
  - 4. セキュアな土台（Cloud Workstations）で安全に走らせる
- **Slide 28: Q&A / 参考リソース・ネクストステップ**
  - 公式ドキュメント、リファレンスアーキテクチャ、ハンズオンガイドへのリンク。

---

## 4. 社内スライドからの主な置換・最適化マップ

| 元スライド（社内 Elevate 研修） | 社外向け Antigravity 研修での置換・方針 |
| :--- | :--- |
| **Jetski** | **Google Antigravity**（または Antigravity CLI / Code OSS） |
| **Jetski Hub / Cloudtop** | **Google Cloud Workstations**（エンタープライズ標準のセキュア開発基盤） |
| **google3 / Piper / CitC / Critique** | **Git / GitHub / GitLab**（一般的なエンタープライズ構成管理） |
| **LOAS / gcert / corpagent** | **Google Cloud IAM / Workload Identity Federation / サービスアカウント** |
| **UDL / Salesforce 社内 MCP** | **Google Cloud マネージド MCP（BigQuery, Cloud Storage, AlloyDB 等）** |
| **社内専用ツール（Moma, Code Search）** | **公式ドキュメント検索, ローカルコード探索 (grep/find), Web 検索** |
| **CE 業務の自動化（商談, 議事録）** | **実践的な業務開発（マイクロサービス化, IaC生成, ユニットテスト自動化）** |
