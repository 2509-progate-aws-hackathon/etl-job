# プロジェクト概要

このリポジトリは、AWS CloudFormation と GitHub Actions を用いて、VPC・Aurora Serverless v2・Lambda（Python）・S3 バケットを自動構築・CI/CD デプロイするサンプルプロジェクトです。

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
requirements.txt # 共通依存
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

```yaml
# ...省略（deploy.yaml参照）
```

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

## 注意事項・ベストプラクティス

- スタック間の値連携は Outputs→GitHub Actions で取得 → 次のデプロイのパラメータに渡す
- Secrets は Secrets Manager で自動生成・管理
- Lambda の依存パッケージは requirements.txt で管理し、zip 化して S3 にアップロード
- S3 バケットと Lambda 関数のデプロイは分離（2 段階デプロイ）
- 削除保護（DeletionProtection）は false なので誤削除に注意

---

## 参考

- [AWS CloudFormation 公式ドキュメント](https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/Welcome.html)
- [GitHub Actions for AWS](https://github.com/aws-actions)
