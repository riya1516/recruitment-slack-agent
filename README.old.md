# 採用選考支援AIエージェント（Slack Bot）

採用部門での書類選考を支援するSlack Bot。履歴書・職務経歴書（PDF）をアップロードするだけで、AIが自動的に評価を行います。

## 🚀 クイックスタート

### ローカル環境で試す（推奨）

1. **setup.bat** をダブルクリック（初回のみ）
2. **backend\.env** を編集してSlackトークンを設定
3. **start.bat** をダブルクリックして起動

詳しい手順は **[QUICKSTART.md](QUICKSTART.md)** を参照してください。

### クラウドにデプロイする

Renderなどのクラウドサービスにデプロイする場合は **[DEPLOY.md](DEPLOY.md)** を参照してください。

## 機能（MVP版）

### 書類選考支援
- PDFファイルから履歴書・職務経歴書を自動解析
- 募集要項に基づいた客観的な評価
- 以下の4つの観点で評価:
  - 技術スキル（必須・優遇スキルとの合致度）
  - 経験の質（プロジェクト経験、成果）
  - 文化適合性（企業価値観との一致）
  - 成長可能性（学習意欲、適応力）
- 評価結果は読みやすいテキスト形式とJSON形式で出力
- 次の面接で確認すべきポイントも提案

## 技術スタック

- **AI**: Google Gemini API (gemini-2.0-flash-exp)
- **Bot Framework**: Slack Bolt for Python
- **PDF解析**: PyPDF2, pdfplumber
- **言語**: Python 3.9+

## セットアップ

### 1. 前提条件

- Python 3.9以上
- Slackワークスペースの管理者権限
- Google Gemini API Key

### 2. Slack Appの作成

1. https://api.slack.com/apps にアクセス
2. "Create New App" → "From scratch" を選択
3. App名と対象ワークスペースを設定

#### 必要な権限（OAuth & Permissions）

Bot Token Scopesに以下を追加:
- `app_mentions:read` - メンションを読み取る
- `chat:write` - メッセージを送信
- `files:read` - アップロードされたファイルを読み取る
- `files:write` - ファイルをアップロード

#### Socket Modeの有効化

1. "Socket Mode" を有効化
2. App-Level Tokenを生成（`connections:write` スコープ）

#### イベントサブスクリプション

"Event Subscriptions" で以下を有効化:
- `app_mention` - ボットがメンションされた時
- `file_shared` - ファイルがアップロードされた時
- `message.channels` - チャンネルメッセージ

### 3. プロジェクトのセットアップ

```bash
# リポジトリをクローン（または作成）
cd recruitment-slack-agent/backend

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example` をコピーして `.env` を作成:

```bash
cp .env.example .env
```

`.env` ファイルを編集して、以下の値を設定:

```env
# Slack Bot Token（xoxb-で始まる）
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Slack App Token（xapp-で始まる）
SLACK_APP_TOKEN=xapp-your-app-token-here

# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here
```

#### APIキーの取得方法

**Slack Bot Token & App Token:**
- Slack App管理画面 → "OAuth & Permissions" → "Bot User OAuth Token"
- "Basic Information" → "App-Level Tokens"

**Gemini API Key:**
- https://makersuite.google.com/app/apikey にアクセス
- "Create API Key" をクリック

### 5. 募集要項のカスタマイズ（オプション）

`app/knowledge/job_requirements.json` を編集して、自社の募集要項に合わせてカスタマイズできます。

```json
{
  "job_title": "ソフトウェアエンジニア",
  "required_skills": [
    "Python経験2年以上",
    ...
  ],
  "company_values": [
    "顧客志向",
    ...
  ]
}
```

## 起動方法

```bash
cd backend/app
python main.py
```

起動すると以下のようなメッセージが表示されます:

```
✅ 採用選考支援Slackボットを起動しています...
📋 書類選考支援機能が有効です
🔌 Slackに接続中...
⚡️ Bolt app is running!
```

## 使い方

### 1. Slackワークスペースにボットを追加

1. Slackワークスペースで採用選考用のチャンネルを作成（例: `#recruitment-screening`）
2. チャンネルにボットを招待: `/invite @YourBotName`

### 2. 書類選考の実行

1. 候補者の履歴書・職務経歴書（PDF）をチャンネルにアップロード
2. ボットが自動的にPDFを解析し、評価結果を返します（通常30秒～1分）

### 3. コマンド

- `@bot help` - 使い方ヘルプを表示
- `@bot 募集要項` - 現在の募集要項を表示

## プロジェクト構造

```
recruitment-slack-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                    # Slackボットのメインロジック
│   │   ├── services/
│   │   │   ├── gemini_service.py      # Gemini API連携
│   │   │   ├── pdf_parser.py          # PDF解析
│   │   │   └── evaluator.py           # 書類選考評価ロジック
│   │   └── knowledge/
│   │       ├── job_requirements.json  # 募集要項
│   │       └── evaluation_template.json # 評価フォーマット
│   ├── requirements.txt               # Python依存関係
│   └── .env.example                   # 環境変数テンプレート
└── README.md                          # このファイル
```

## デプロイ（Renderへの簡単デプロイ）

### シンプル版（AI機能なし）のデプロイ

まずは基本的なSlack Bot機能のみをデプロイし、後でAI機能を追加できます。

#### 1. GitHubリポジトリの準備

```bash
cd recruitment-slack-agent

# Gitリポジトリを初期化（まだの場合）
git init

# ファイルを追加
git add .
git commit -m "Initial commit: Recruitment Slack Bot"

# GitHubにプッシュ（リポジトリを作成済みの場合）
git remote add origin https://github.com/your-username/recruitment-slack-agent.git
git branch -M main
git push -u origin main
```

#### 2. Renderでのデプロイ

1. **Renderアカウント作成**
   - https://render.com にアクセス
   - GitHubアカウントでサインアップ

2. **新規サービス作成**
   - "New" → "Background Worker" を選択
   - GitHubリポジトリを接続
   - `recruitment-slack-agent` を選択

3. **デプロイ設定**
   - **Name**: `recruitment-slack-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements_simple.txt`
   - **Start Command**: `python backend/app/main_simple.py`

4. **環境変数を設定**
   - `SLACK_BOT_TOKEN`: Slack Bot Token（xoxb-...）
   - `SLACK_APP_TOKEN`: Slack App Token（xapp-...）

5. **デプロイ実行**
   - "Create Background Worker" をクリック
   - 自動的にデプロイが開始されます

#### 3. 動作確認

- Renderのログで起動を確認
- Slackでボットにメンションして動作確認
- PDFファイルをアップロードして受付確認

#### 4. AI機能の追加（後日）

AI機能を追加する場合:

1. 環境変数に `GEMINI_API_KEY` を追加
2. Start Commandを `python backend/app/main.py` に変更
3. Build Commandを `pip install -r backend/requirements.txt` に変更
4. 再デプロイ

### 注意事項

- Renderの無料プランは15分アクティビティがないとスリープします
- Slack Socket Modeは常時接続が必要なため、有料プラン（$7/月〜）推奨
- 本番運用前に動作テストを十分に行ってください

## 今後の拡張（フルスペック版）

- 一次面接支援: 面接議事録の解析、カルチャーフィット評価
- 二次面接支援: コンピテンシー評価、スキル深掘り
- 最終面接支援: 経営層視点での評価、違和感の言語化
- データベース連携: 候補者情報の永続化
- ダッシュボード: Web UIでの評価結果確認

## トラブルシューティング

### ボットが反応しない

1. `.env` ファイルの設定を確認
2. Slackのイベントサブスクリプションが有効か確認
3. ボットがチャンネルに招待されているか確認

### PDF解析に失敗する

- 画像ベースのPDF（スキャン画像）は解析できません
- テキスト形式のPDFをご使用ください

### Gemini APIエラー

- APIキーの有効性を確認
- Google Cloud Consoleで Gemini API が有効化されているか確認
- APIの利用上限を確認

## ライセンス

MIT License

## サポート

問題が発生した場合は、以下を確認してください:
- ログ出力を確認
- 環境変数の設定を再確認
- Slack App設定を再確認

それでも解決しない場合は、開発チームにお問い合わせください。
