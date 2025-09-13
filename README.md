# プロジェクト概要

このリポジトリは、AWS CloudFormation と GitHub Actions を用いて、VPC・Aurora Serverless v2・Lambda（Python）・S3 バケットを自動構築・CI/CD デプロイするプロジェクトです。

---

## ディレクトリ構成

```
infra/
  network.yaml   # VPC, サブネット, NAT, SG
  rds.yaml       # Aurora Serverless v2, Secrets Manager
  s3.yaml        # Lambda用S3バケット
  lambda.yaml    # Lambda関数本体
  README.md      # テンプレート解説
scripts/
  create_table/
    lambda.py
    requirements.txt
  insert_table/
    lambda.py
    requirements.txt
.github/
  deploy.yaml    # GitHub Actionsワークフロー
```

---

## デプロイ全体フロー（CI/CD）

1. **VPC/サブネット/SG の作成**（network.yaml）
2. **Aurora RDS クラスタの作成**（rds.yaml）
   - Secrets Manager で DB 認証情報を自動生成
   - Outputs からエンドポイント・ポート・Secrets ARN を取得
3. **Lambda 用 S3 バケットの作成**（s3.yaml）
4. **Lambda パッケージのビルド・S3 アップロード**
5. **Lambda 関数のデプロイ**（lambda.yaml）
   - RDS 接続情報・Secrets ARN 等は Outputs から自動連携

---

## GitHub Actions ワークフロー例

`.github/deploy.yaml` で全自動デプロイが可能です。

- VPC/サブネット/SG/RDS/Lambda/S3 の全リソースを一括デプロイ
- RDS の Outputs（エンドポイント・Secrets ARN 等）を自動取得し、Lambda のパラメータに連携
- Lambda パッケージは requirements.txt で依存解決し zip 化 →S3 アップロード

---

## 主要 CloudFormation テンプレートのポイント

### network.yaml

- 2AZ 構成の VPC/サブネット/NAT/SG を作成
- Outputs で VPC ID・サブネット ID・SG ID をエクスポート

### rds.yaml

- Aurora Serverless v2（PostgreSQL）クラスタ＋ Secrets Manager
- DB 認証情報は自動生成し Secrets Manager に格納
- Outputs で DB エンドポイント・ポート・Secrets ARN 等を出力

### s3.yaml

- Lambda コード格納用の S3 バケットを作成
- Outputs でバケット名を出力

### lambda.yaml

- Lambda 関数（create_table, insert_table）をデプロイ
- S3 バケット名・zip キー・RDS 接続情報・Secrets ARN 等をパラメータで受け取る
- VPC 内配置・SecretsManager/RDS へのアクセス権限付与

---

---

## アーキテクチャ図

本プロジェクトの AWS インフラ構成は以下の通りです。

![AWSアーキテクチャ図](infra/architecture/aws-architecture.svg)

### 構成要素の説明

- **VPC/サブネット/SG**: 2AZ 構成の VPC 内にパブリック・プライベートサブネット、NAT Gateway、セキュリティグループを配置
- **Aurora Serverless v2 (RDS)**: プライベートサブネット内に Aurora クラスタを構築し、Secrets Manager で認証情報を管理
- **Lambda 関数**: create_table/insert_table の ETL 用 Lambda を Aurora と同じ VPC 内にデプロイ
- **S3 バケット**: Lambda コード(zip)の格納用
- **GitHub Actions & CloudFormation**: CI/CD パイプラインで CloudFormation テンプレートを用いて全リソースを自動構築

この構成により、セキュアかつ自動化されたデータ処理基盤を AWS 上に構築できます。
