# Antigravity on Cloud Workstations ハンズオン環境セットアップガイド

[Cloud Workstations](https://cloud.google.com/workstations) 上に [Antigravity](https://antigravity.google/)（AI コーディングエージェント）を構成し、セキュアなクラウド環境（ローカル端末へのソースコード非保持）でハンズオンを実施するためのエンタープライズ向けリファレンス構成です。

---

## 1. 全体アーキテクチャ & 構成要素

```
+-----------------------------------------------------------------------------------+
| [クライアント端末 (社内PC)]                                                        |
|   1. Webブラウザ (推奨: 完全Web完結) --------+                                    |
|   2. ローカル VS Code (Remote-SSH) ---+      |                                    |
+---------------------------------------|------|------------------------------------+
                                        |      | (HTTPS / IAPトンネル)
                                        v      v
+-----------------------------------------------------------------------------------+
| Google Cloud 境界 (貴社 GCP プロジェクト)                                          |
|                                                                                   |
|  [Cloud Workstations クラスター]                                                   |
|    └─ Workstation VM (Private VPC, Zero Public IP)                                |
|         └─ コンテナ (Code OSS Web IDE + Antigravity CLI)                           |
|              ├─ ソースコード・生成ファイル (永続ディスク上にのみ保管)              |
|              ├─ ライフサイクル管理 (IdleAction.SUSPEND によるメモリ保持・停止)    |
|              └─ 認証 (VM サービスアカウントによる IAM/ADC 認証: APIキー不要)      |
|                                        │                                          |
|                                        ▼                                          |
|  [Vertex AI / Gemini Enterprise API] (コード生成バックエンド)                      |
|  [Cloud Logging] (操作ログ・監査トレース)                                          |
+-----------------------------------------------------------------------------------+
```

| レイヤ | リソース / 設計 | 説明 |
|---|---|---|
| **ネットワーク** | Private VPC + Cloud NAT + Private Google Access | VM にパブリック IP を一切持たせず（ゼロパブリック IP）、Cloud NAT 経由で安全にアウトバウンド通信 |
| **ID & 認証** | Workstation 実行用サービスアカウント (SA) | `roles/aiplatform.user` + `cloud-platform` スコープを付与。API キーの払い出し・端末管理が不要 |
| **コンテナ** | Code OSS (Web IDE) + Antigravity CLI | ブラウザ上で VS Code と同等の操作感。エージェント連携済み |
| **ストレージ** | 永続ホームディスク (`pd-balanced` 50GB) | 端末側には一切ファイルを同期せず保持。SSD (pd-balanced) を採用し、200GB の制約を回避して 50GB に軽量化・コスト半減 |
| **ガバナンス** | `IdleAction.SUSPEND` + Cloud Logging | アイドル時は自動サスペンドでコストを抑えつつ、作業コンテキストを維持 |

---

## 2. 前提条件（管理者 vs 受講者の違い）

本ハンズオンでは、**「環境を構築する管理者（講師・事務局）」** と **「ハンズオンに参加する受講者（利用者）」** で必要な前提条件・権限・端末環境が大きく異なります。

| 項目 | 管理者（講師・インフラ担当） | 受講者・利用者（ハンズオン参加者） |
|---|---|---|
| **役割** | クラスター、VPC、構成（Config）、受講者用 Workstation のプロビジョニング | 割り当てられた自分専用のコンテナをブラウザで起動して開発演習 |
| **端末の要件** | ・Google Cloud コンソール操作が可能な Web ブラウザ<br>・（自動化する場合）`gcloud` CLI / `terraform` (v1.6+) または Cloud Shell | **Web ブラウザ（Google Chrome 推奨）のみ**<br>※PC 端末への Git、VS Code、CLI、拡張機能のインストールは一切不要 |
| **必要な IAM 権限** | ・`roles/workstations.admin`（クラスター・構成・インスタンス管理）<br>・`roles/iam.serviceAccountAdmin`（サービスアカウント作成）<br>・`roles/compute.networkAdmin`（VPC・サブネット・Cloud NAT 管理）<br>・`roles/artifactregistry.admin`（カスタムイメージ用） | ・**`roles/workstations.user`**（自分専用の Workstation へのアクセス権）<br>・**`roles/viewer`**（GCP コンソールで一覧画面を表示する場合。直接 URL を開く運用の場合は不要）<br>※他人の環境の閲覧やインフラ設定の変更はできません |
| **Google アカウント** | GCP プロジェクトでリソース構築が可能な組織アカウント | ハンズオンで使用する Google アカウント（`user:participant@example.com`） |

---

## 3. GCP 事前準備（API の有効化）【管理者のみ実施】

Cloud Shell または端末から、管理者アカウントで必要な API を有効化します。受講者の実施は不要です。

```bash
gcloud services enable \
    workstations.googleapis.com \
    compute.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    logging.googleapis.com
```

---

## 4. Google Cloud コンソール（GUI）での構築手順【管理者のみ実施】

Google Cloud コンソール画面（Web GUI）からマウス操作のみでセットアップする標準手順です。
以下の **5 つのステップ** の順序で作成します（Terraform で一括自動構築する場合は「[5. Terraform によるインフラ自動構築（IaC）](#5-terraform-によるインフラ自動構築iac管理者のみ実施)」を参照してください）。

```
[ステップ 1: VPC ネットワーク & Cloud NAT の作成]（ゼロパブリックIP通信基盤）
         │
         ▼
[ステップ 2: サービスアカウントの作成]（API キー不要化）
         │
         ▼
[ステップ 3: ワークステーション クラスターの作成]（約10〜15分）
         │
         ▼
[ステップ 4: ワークステーション 構成（Config）の作成]（マシン・セキュリティ設定）
         │
         ▼
[ステップ 5: ワークステーション（インスタンス）の作成 & 起動]（受講者ごとの環境）
```

---

### ステップ 1: VPC ネットワーク & Cloud NAT の作成（ゼロパブリック IP 通信基盤）

Workstation VM にパブリック IP を持たせない（ゼロパブリック IP）セキュアな構成にするため、専用 VPC と外部インターネット通信用の Cloud NAT を作成します。

> [!TIP]
> **既存の社内 VPC を利用する場合**:
> すでにインターネットへのアウトバウンド通信経路（Cloud NAT 等）および「限定公開の Google アクセス（Private Google Access）」が有効化されている既存 VPC / サブネットがある場合は、本ステップをスキップして **ステップ 2** へ進んでください。

#### 1-1. VPC ネットワークの作成（自動モード） & 限定公開の Google アクセスの有効化

1. Google Cloud コンソールで **[VPC ネットワーク]** > **[VPC ネットワーク]** を開きます。
2. 上部の **[+ VPC ネットワークを作成]** をクリックします。
3. 以下の項目を設定します：
   - **名前**: `antigravity-ws-vpc`
   - **サブネットの作成モード**: **「自動」** を選択（全リージョンにサブネットが自動作成され、CIDR 設計の手間なくシンプルに構築できます）
   - **ファイアウォール ルール**: デフォルトのまま（または社内ポリシーに応じて選択）
4. **[作成]** をクリックします。
5. 作成完了後、一覧から作成した **`antigravity-ws-vpc`** をクリックして詳細画面を開きます。
6. **[サブネット]** タブを開き、今回使用するリージョン（**`asia-northeast1`**）のサブネット名をクリックします。
7. 上部の **[編集]** をクリックし、**「限定公開の Google アクセス (Private Google Access)」** を **「オン」** に変更して **[保存]** をクリックします。
   （※パブリック IP を持たない VM から Vertex AI 等の Google Cloud API へアクセスするために必須です）

#### 1-2. Cloud Router & Cloud NAT の作成（外部インターネット通信用）

Workstation 内からのパッケージ取得（`apt` や `npm`、`pip` 等）や外部通信を安全に行うため、Cloud NAT を構成します。

1. コンソールで **[ネットワーク サービス]** > **[Cloud NAT]** を開きます。
2. 上部の **[+ Cloud NAT ゲートウェイを作成]**（初回は **[開始]**）をクリックします。
3. 以下の項目を設定します：
   - **ゲートウェイ名**: `antigravity-ws-nat`
   - **ネットワーク**: ステップ 1-1 で作成した **`antigravity-ws-vpc`** を選択
   - **リージョン**: **`asia-northeast1 (東京)`** を選択
   - **Cloud Router**: **[新しいルーターを作成]** を選択し、名前に `antigravity-ws-router` を入力して **[作成]** をクリック
   - **NAT マッピング（ソース）**: **「すべてのサブネット（プライマリとセカンダリ）」**（デフォルト）を選択
   - **NAT IP アドレス**: **「自動（推奨）」** を選択
4. **[作成]** をクリックします。

---

### ステップ 2: サービスアカウントの作成（API キー不要化）
Workstations 内から Vertex AI への認証を安全に行うためのサービスアカウントを用意します。

1. Google Cloud コンソールで **[IAM と管理]** > **[サービス アカウント]** を開きます。
2. 上部の **[+ サービス アカウントを作成]** をクリックします。
   - **サービス アカウント名**: `antigravity-ws-sa`
   - **サービス アカウント ID**: 自動入力されます（`antigravity-ws-sa`）。
   - **[作成して続行]** をクリックします。
3. **[このサービス アカウントにプロジェクトへのアクセスを許可する]** で以下の 2 つのロールを付与します：
   - **`Vertex AI ユーザー`** (`roles/aiplatform.user`)
   - **`ログ書き込み`** (`roles/logging.logWriter`)
4. **[完了]** をクリックします。

---

### ステップ 3: ワークステーション クラスターの作成
Workstations をホストするクラスター基盤を作成します。

1. コンソールで **[Cloud Workstations]** > **[クラスター管理]** を開きます。
2. 上部の **[+ クラスターを作成]** をクリックします。
3. 以下の項目を設定します：
   - **名前**: `antigravity-cluster`
   - **リージョン**: `asia-northeast1 (東京)`
   - **ネットワーク**:
     - **ネットワーク**: ステップ 1 で作成した **`antigravity-ws-vpc`**（または既存の社内 VPC）を選択
     - **サブネットワーク**: **`antigravity-ws-vpc (asia-northeast1)`**（または既存のサブネット）を選択
   - **プライベート クラスター**: チェックを入れない（または社内規約に応じて選択）
4. **[作成]** をクリックします。
   > [!NOTE]
   > クラスターのプロビジョニングには **約 10 〜 15 分** かかります。ステータスが「準備完了 (緑のチェック)」になるまで待ちます。

---

### ステップ 4: ワークステーション構成（Config）の作成
マシンタイプ、セキュリティ、自動サスペンド、IDE コンテナを定義します。

1. コンソールで **[Cloud Workstations]** > **[ワークステーションの構成]** を開きます。
2. 上部の **[+ ワークステーション構成を作成]** をクリックします。
3. **基本情報**:
   - **構成名**: `antigravity-config`
   - **クラスター**: ステップ 3 で作成した `antigravity-cluster` を選択
4. **マシンの構成**:
   - **マシンタイプ**: `e2-standard-4`（4 vCPU, 15 GB メモリ / 標準構成）
   - **アイドル時のシャットダウン**: **「30 分」** を選択（コスト保護）
   - **シャットダウン時のアクション**: **「サスペンド」** を選択（作業中のメモリ状態を保持して停止）
5. **環境のカスタマイズ**:
   - **環境**: **「ベース定義済みイメージ」** を選択
   - **コード エディタ**: **「Code OSS（Cloud Workstations で提供）」** を選択
     （※最新の Code OSS イメージには Antigravity / Gemini CLI が標準プリインストールされています）
6. **ストレージの設定**:
   - **ホーム ディレクトリのディスク タイプ**: **「バランス型永続ディスク (pd-balanced)」**
   - **ディスク サイズ**: **`50 GB`**（十分な容量を確保しつつディスク費用を半減）
   - **再利用ポリシー**: **「削除」**（演習終了時にディスクも自動解放する場合）
7. **詳細設定 (セキュリティ & ID)**:
   - **サービス アカウント**: ステップ 2 で作成した `antigravity-ws-sa` を選択
   - **パブリック IP アドレスを無効にする**: **チェックを入れる**（ゼロパブリック IP 化）
8. **[作成]** をクリックします。

---

### ステップ 5: ワークステーションの作成 & 起動
受講者が実際に作業する個別インスタンスを作成します。

1. コンソールで **[Cloud Workstations]** > **[ワークステーション]** を開きます。
2. 上部の **[+ ワークステーションを作成]** をクリックします。
3. 以下の項目を設定します：
   - **ワークステーション名**: `participant-workstation`（または受講者名 `ws-user01` 等）
   - **構成**: ステップ 4 で作成した `antigravity-config` を選択
4. **[作成]** をクリックします。（約 1 〜 2 分で作成されます）
5. 作成後、一覧画面で対象ワークステーションの **[起動]** をクリックします。
6. ステータスが「実行中」になったら、**[開く]** をクリックすると、新しいブラウザタブで Code OSS（Web IDE）が立ち上がります。

---

## 5. Terraform によるインフラ自動構築（IaC）【管理者のみ実施】

コンソールからの手動構築の代わりに、Terraform を用いて VPC、Cloud NAT、サービスアカウント、クラスター、構成（Config）、および複数受講者のワークステーションを一括でコード管理・自動構築する場合の手順です。

お客様の環境に合わせて、以下の **2つのネットワーク構成パターン** に対応しています：
- **パターン 1: 既存の社内 VPC / サブネットを利用する場合**
  - `terraform.tfvars` に既存 VPC 名とサブネット名を指定するだけで、既存ネットワーク内に Workstations を相乗り構築します。
- **パターン 2: ハンズオン専用の Private VPC を新規作成する場合**
  - 変数を空のままにすると、専用 VPC、プライベートサブネット（Private Google Access 有効）、および Cloud NAT が自動プロビジョニングされます。

### `terraform.tfvars` 設定例
```hcl
project_id       = "YOUR_PROJECT_ID"
region           = "asia-northeast1"
workstation_users = [
  "user:participant01@example.com",
  "user:participant02@example.com"
]

# --- パターン 1: 既存の社内 VPC を利用する場合 ---
existing_network    = "projects/YOUR_PROJECT_ID/global/networks/existing-vpc"
existing_subnetwork = "projects/YOUR_PROJECT_ID/regions/asia-northeast1/subnetworks/existing-subnet"

# --- パターン 2: 専用 VPC を新規作成する場合は上記 2 行をコメントアウト ---
```

### `main.tf`
```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" { type = string }
variable "region" { default = "asia-northeast1" }
# 受講者のメールアドレスリスト（複数名対応）
variable "workstation_users" {
  type        = list(string)
  default     = ["user:participant01@example.com", "user:participant02@example.com"]
  description = "受講者の Google アカウント一覧 (user:xxx@example.com)"
}

# クイックスタートプール台数（0 = プールなし、5 = 5台常時待機）
variable "quick_start_pool_size" {
  type        = number
  default     = 0
  description = "事前スタンバイ台数（ハンズオン直前に 5〜10 に変更して apply すると即時起動可能）"
}

# 既存 VPC を使用する場合の設定（空文字の場合は新規 VPC / サブネットを作成）
variable "existing_network" {
  type        = string
  default     = ""
  description = "既存の VPC ネットワーク名（例: projects/PROJECT_ID/global/networks/my-vpc）"
}

variable "existing_subnetwork" {
  type        = string
  default     = ""
  description = "既存の サブネット名（例: projects/PROJECT_ID/regions/REGION/subnetworks/my-subnet）"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. ネットワーク (新規作成する場合のみ適用)
locals {
  create_network = var.existing_network == ""
  network_id     = local.create_network ? google_compute_network.ws_vpc[0].id : var.existing_network
  subnetwork_id  = local.create_network ? google_compute_subnetwork.ws_subnet[0].id : var.existing_subnetwork
}

resource "google_compute_network" "ws_vpc" {
  count                   = local.create_network ? 1 : 0
  name                    = "antigravity-ws-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "ws_subnet" {
  count                    = local.create_network ? 1 : 0
  name                     = "antigravity-ws-subnet"
  ip_cidr_range            = "10.10.0.0/20"
  region                   = var.region
  network                  = google_compute_network.ws_vpc[0].id
  private_ip_google_access = true
}

# 新規 VPC 作成時の Cloud Router & Cloud NAT
resource "google_compute_router" "ws_router" {
  count   = local.create_network ? 1 : 0
  name    = "antigravity-ws-router"
  region  = var.region
  network = google_compute_network.ws_vpc[0].id
}

resource "google_compute_router_nat" "ws_nat" {
  count                              = local.create_network ? 1 : 0
  name                               = "antigravity-ws-nat"
  router                             = google_compute_router.ws_router[0].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# 2. サービスアカウント (APIキー不要で Vertex AI を利用)
resource "google_service_account" "ws_sa" {
  account_id   = "antigravity-ws-sa"
  display_name = "Cloud Workstations Antigravity Service Account"
}

resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.ws_sa.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.ws_sa.email}"
}

# 3. Artifact Registry (カスタムイメージ用)
resource "google_artifact_registry_repository" "ws_repo" {
  location      = var.region
  repository_id = "workstations-images"
  format        = "DOCKER"
}

# 4. Cloud Workstations クラスター
resource "google_workstations_workstation_cluster" "ws_cluster" {
  workstation_cluster_id = "antigravity-cluster"
  network                = local.network_id
  subnetwork             = local.subnetwork_id
  location               = var.region
}

# 5. Cloud Workstations 構成 (サスペンド対応・自動停止設定)
resource "google_workstations_workstation_config" "ws_config" {
  workstation_config_id  = "antigravity-config"
  workstation_cluster_id = google_workstations_workstation_cluster.ws_cluster.workstation_cluster_id
  location               = var.region

  idle_timeout = "1800s" # 30分アイドルで自動停止/サスペンド（作業内容は保持）
  running_timeout = "28800s" # 8時間でセッション終了

  host {
    gce_instance {
      machine_type                = "e2-standard-2" # 2 vCPU, 8 GB メモリ（最小コスト推奨構成）
      service_account             = google_service_account.ws_sa.email
      service_account_scopes      = ["https://www.googleapis.com/auth/cloud-platform"]
      disable_public_ip_addresses = true # 完全プライベートIP構成（外部通信は Cloud NAT 経由）
      pool_size                   = var.quick_start_pool_size # 事前プール台数（0なら完全オンデマンド）
    }
  }

  persistent_directories {
    mount_path = "/home"
    gce_pd {
      disk_type      = "pd-balanced" # バランス型 SSD を採用し、200GB の制約を回避
      size_gb        = 50            # 50GB に縮小（ディスク課金を大幅削減）
      fs_type        = "ext4"
      reclaim_policy = "DELETE" # ワークステーション本体を削除した際にディスクを解放（一時停止時は保持されます）
    }
  }

  # Cloud Workstations 標準 Code OSS（Antigravity / Gemini CLI バンドル済み）コンテナ
  container {
    image = "${var.region}-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest"
  }

  replica_zones = ["asia-northeast1-a", "asia-northeast1-b"]
}

# 6. 受講者用 Workstation（複数受講者向け一括作成 & 個別権限付与）
resource "google_workstations_workstation" "attendee_ws" {
  for_each               = toset(var.workstation_users)
  workstation_id         = "ws-${replace(replace(split(":", each.key)[1], "@", "-"), ".", "-")}" # 例: ws-user01-example-com
  workstation_config_id  = google_workstations_workstation_config.ws_config.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.ws_cluster.workstation_cluster_id
  location               = var.region
}

# 各受講者に、自分専用のワークステーションのみを起動・利用できる権限を付与
resource "google_workstations_workstation_iam_member" "attendee_iam" {
  for_each               = toset(var.workstation_users)
  workstation_id         = google_workstations_workstation.attendee_ws[each.key].workstation_id
  workstation_config_id  = google_workstations_workstation_config.ws_config.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.ws_cluster.workstation_cluster_id
  location               = var.region
  role                   = "roles/workstations.user"
  member                 = each.key
}
```

### Terraform の実行手順（プロビジョニング手順）

作成した `main.tf` と `terraform.tfvars` があるディレクトリで以下のコマンドを実行します。

#### 1. 認証と初期化 (Init)
Google Cloud へのログインと、Terraform プロバイダプラグインのダウンロードを行います。

```bash
# Google Cloud にログインして Application Default Credentials (ADC) を取得
gcloud auth application-default login

# Terraform プロバイダとバックエンドの初期化
terraform init
```

#### 2. 実行計画の確認 (Plan)
作成されるリソース（VPC/サブネット、サービスアカウント、クラスター、構成、ワークステーション）を確認します。

```bash
terraform plan
```
> [!TIP]
> 既存の VPC を使用する場合は、`existing_network` と `existing_subnetwork` が渡され、新規 VPC 関連リソースが作成されない（Plan で 0 to add になる）ことを確認してください。

#### 3. リソースの作成・適用 (Apply)
リソースをプロビジョニングします。

```bash
terraform apply
```
確認プロンプトが表示されたら `yes` と入力してエンターキーを押します。
（クラスターと構成の作成には約 15〜20 分程度かかります）

#### 4. ハンズオン終了後のリソース削除 (Destroy)
演習がすべて終了し、環境をクリーンアップする場合は以下を実行します。

```bash
# ワークステーション環境を一括破棄
terraform destroy
```
確認プロンプトで `yes` と入力すると、作成された Cloud Workstations リソースおよび専用 VPC（新規作成した場合）が安全に解放されます。

---

## 6. コンテナ定義とビルド（Cloud Build）【※通常はスキップ可能・アドバンスド】

> [!IMPORTANT]
> **【通常は本セクション（カスタム Docker ビルド）の実施は不要です】**
> 1. **標準イメージで Antigravity / Gemini CLI が利用可能**: Cloud Workstations の標準イメージ（`code-oss:latest`）には、最初から **Antigravity CLI (`agy`)** および **Gemini CLI (`gemini`)** がプリインストールされています。
> 2. **`agents-cli` (`google-agents-cli`) も Docker 変更なしで永続化可能**: Cloud Workstations では `/home`（`/home/user`）領域が **永続ディスク（Persistent Disk 50GB）** としてマウントされます。そのため、受講者が初回起動時にターミナルで 1 行セットアップコマンド（`uv` および `google-agents-cli` のインストール）を実行するだけで、コンテナの再起動やサスペンド後もツール・ADK スキル一式（`~/.gemini/` 等）がそのまま永続保持されます。
>
> ※もし `Dockerfile` ビルド時に `/home/user` 配下へツールをインストールしても、ワークステーション起動時に空の `/home` 永続ディスクが上からマウント（上書きマスク）されて消えてしまう点に注意してください。カスタムイメージに事前組み込みする場合は、以下の例のように `/usr/local` などのシステム領域へ配置するか、`/etc/workstation-startup.d/` の起動スクリプトを使用します。

### カスタムイメージを作成する場合の `Dockerfile` 例（システム領域へのプリインストール）
標準の Code OSS（Web IDE）をベースに、`uv` や `google-agents-cli` 等をシステム領域（`/usr/local`）へ事前組み込みする場合の構成例です。

```dockerfile
FROM us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest

USER root
ENV DEBIAN_FRONTEND=noninteractive

# 基本ツールのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    build-essential \
    git \
    jq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# uv および google-agents-cli をシステム共通領域 (/usr/local) にインストール
# ※ /home 配下にインストールすると永続ディスクマウント時に隠蔽されるため環境変数でインストール先を指定
ENV UV_INSTALL_DIR="/usr/local/bin" \
    UV_TOOL_BIN_DIR="/usr/local/bin" \
    UV_TOOL_DIR="/opt/uv-tools"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv tool install google-agents-cli

# コンテナ起動時に受講者の /home/user へ ADK スキル一式 (agents-cli setup) を自動展開するスタートアップスクリプト
RUN mkdir -p /etc/workstation-startup.d && \
    cat << 'EOF' > /etc/workstation-startup.d/110_setup_agents_cli.sh
#!/bin/bash
# 初回起動時のみ /home/user に ADK スキル一式を展開
if [ ! -f /home/user/.agents_cli_initialized ]; then
  su - user -c "uvx google-agents-cli setup"
  touch /home/user/.agents_cli_initialized
fi
EOF
RUN chmod +x /etc/workstation-startup.d/110_setup_agents_cli.sh

# Workstations 標準ユーザーに戻す
USER user
WORKDIR /home/user
```

### ビルドの実行（Cloud Build）
```bash
gcloud builds submit . \
  --tag=asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/workstations-images/antigravity-ide:latest
```

---

## 7. 接続方法 & 運用モデル（管理者と受講者の役割分担）

### 7.1. 運用モデルの全体像：「管理者が土台を用意し、受講者はコンテナを起動するだけ」

Cloud Workstations の最大の特長は、**インフラ構築の負担がすべて管理者に集約され、受講者はブラウザを開いて自分の「コンテナ」を起動するだけで済む** 点にあります。

受講者の PC 端末には開発ツールのインストールも、GCP の難しいコマンド操作も一切不要です。

```
【管理者（講師・事務局）が事前にやること】
 1. ネットワーク & クラスターの作成（共通インフラの用意）
 2. ワークステーション構成（Config）の定義（Antigravity 搭載コンテナイメージ・マシンスペックを指定）
 3. 受講者人数分のワークステーション枠を作成し、各受講者に IAM 権限を付与
      │
      ▼（受講者へは「Workstations コンソールの URL」を案内するだけ）
      │
【受講者（参加者）がハンズオン当日にやること】
 1. 案内された URL をブラウザで開く
 2. 自分専用のワークステーションの [起動] をクリック（コンテナが立ち上がる）
 3. [開く] をクリックすると、ブラウザ上に VS Code (Code OSS) が全画面で起動！
 4. 初回のみターミナルで 1 行セットアップを実行し、すぐに Antigravity × agents-cli による開発を開始！
```

---

| 役割 | 担当作業 | 受講者・管理者の体験 |
| :--- | :--- | :--- |
| **管理者 (Admin)** | **クラスター ＆ 構成 (Config) の作成** | ・ネットワーク（VPC）やセキュリティ境界を一元管理<br>・全受講者が使う「共通コンテナイメージ」やマシンタイプを定義<br>・受講者ごとに専用のワークステーションを払い出す |
| **受講者 (Attendee)** | **自分のコンテナを「起動」して「開く」だけ** | ・PC には何もインストール不要（Chrome 等のブラウザのみ）<br>・コンソール画面で **[起動] ➜ [開く]** を押すだけでコンテナが起動<br>・他人のコンテナやソースコードはお互いに見えず、完全隔離 |

---

### 7.2. 複数ワークステーションの事前プロビジョニング【管理者のみ実施】

管理者（代表者）は、ハンズオン前日までに以下のコマンドまたはコンソール画面から人数分のワークステーションを作成しておきます。
（※作成直後は停止状態のため、コンピュート課金は発生しません）

```bash
# 例: 受講者 3 名分のワークステーション枠を一括作成
for USER_ID in user01 user02 user03; do
  gcloud workstations create "ws-${USER_ID}" \
    --cluster=antigravity-cluster \
    --config=antigravity-config \
    --region=asia-northeast1
done

# 各受講者に、自分専用のワークステーションのみを起動・利用できる権限を付与
# (※作成者自身には自動的に roles/workstations.user が付与されます)
cat << 'EOF' > /tmp/ws-policy.yaml
bindings:
- members:
  - user:user01@example.com
  role: roles/workstations.user
EOF
gcloud workstations set-iam-policy ws-user01 /tmp/ws-policy.yaml \
  --cluster=antigravity-cluster \
  --config=antigravity-config \
  --region=asia-northeast1
```

---

### 7.3. 受講者の当日接続ステップ（これだけ案内すればOK）【受講者が実施】

受講者向けの案内文面（チャットやメールで送る内容）は、以下の **4 ステップのみ** で完結します。

> **【受講者向けハンズオン参加手順】**
> 1. Google Chrome 等のブラウザで [Cloud Workstations コンソール](https://console.cloud.google.com/workstations) にアクセスしてください。
> 2. ご自身のアカウント宛に割り当てられたワークステーション（例: `ws-user01`）が表示されますので、**[起動]** をクリックしてください。
> 3. ステータスが「実行中」に変わったら、**[開く]** をクリックしてください。
> 4. ブラウザ上で IDE（VS Code / Code OSS）が開いたら、ターミナル（`Ctrl + ~`）で以下の **初回セットアップコマンド（1行）** を実行してください（`/home` 永続ディスクに保存されるため初回のみで OK です）：
>    ```bash
>    curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.local/bin/env && uv tool install google-agents-cli && uvx google-agents-cli setup
>    ```

### 7.4. 各受講者による接続方法（2 通りの選択肢）【受講者が実施】

#### 方法 A: Webブラウザ経由での接続（推奨：完全Web完結）
受講者の端末に何もインストールせず、ブラウザだけで参加できる形態です。

1. **受講者がコンソールを開く**:
   受講者は Google Cloud Console の [Cloud Workstations 画面](https://console.cloud.google.com/workstations) にアクセスします。
   （権限が付与されている自分専用のワークステーション `ws-userXX` のみが表示されます）
2. **ワークステーションを開く**:
   代表者がすでに起動済みの場合は、そのまま **「開く」** をクリックします。
   （停止している場合は、受講者自身で **「起動」** をクリックし、約 1 分後に **「開く」** をクリックします）
3. **`agents-cli` 初回セットアップ & エージェントの利用開始**:
   * ブラウザ上に VS Code と同様の IDE（Code OSS）が表示されます。
   * 下部の統合ターミナル（`Ctrl + ~`）を開き、初回のみ以下を実行して `uv` と `google-agents-cli`（および Antigravity 向け ADK スキル一式）を導入します：
     ```bash
     # uv の導入 + google-agents-cli インストール + ADK スキル一式のセットアップ
     curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.local/bin/env
     uv tool install google-agents-cli
     uvx google-agents-cli setup
     ```
   * インストール完了後、`agents-cli info` でバージョンを確認し、`agy` または `gemini` を起動してエージェント開発を開始します。（`/home` ディレクトリは永続ディスクにマウントされているため、次回以降の起動時はこの手順は不要です）

---

#### 方法 B: 手元の VS Code からのリモート接続（Remote-SSH 方式）
手元の VS Code アプリの UI を使いつつ、ファイルの実体や実行環境は 100% クラウドに置く形態です。

1. **SSH トンネルの開始（受講者の端末ターミナル）**:
   ```bash
   gcloud workstations start-tcp-tunnel ws-user01 22 \
     --cluster=antigravity-cluster \
     --config=antigravity-config \
     --region=asia-northeast1 \
     --local-host-port=:2222
   ```
2. **SSH 設定（`~/.ssh/config`）**:
   ```ssh
   Host antigravity-ws
       HostName localhost
       Port 2222
       User user
       StrictHostKeyChecking no
       UserKnownHostsFile /dev/null
   ```
3. **VS Code から接続**:
   * VS Code の「Remote - SSH」拡張機能を開き、`antigravity-ws` に接続します。
   * **メリット**: 端末側にはファイルは作成されず、クラウド上のファイルを直接編集・操作できます。

---

## 8. セキュリティ & ガバナンスのポイント

- **コード・データのローカル非保持**:
  - すべてのコード生成、ファイル保存、ビルド実行は Workstation VM 上の永続ディスク内で完結します。ローカル端末側へのダウンロード制御やクリップボード制限も GCP 側で構成可能です。
- **認証情報の保護（APIキーの廃止）**:
  - Workstation VM にアタッチされたサービスアカウントが自動的に認証（ADC）を行うため、受講者に API キーやシークレット情報を配布する必要がありません。
- **コスト保護（自動サスペンド）**:
  - 30分間操作がない場合、自動的にインスタンスがサスペンドされ、vCPU/メモリ課金が停止します。再接続時には作業状態がそのまま復旧します。
