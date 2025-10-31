# クイックスタート（ローカル環境）

このガイドでは、ローカル環境（localhost）でSlack Botを起動する方法を説明します。

## 📋 前提条件

- Windows PC
- Python 3.9以上がインストール済み
- Slackワークスペースの管理者権限

## 🚀 5分でセットアップ

### ステップ1: Slack Appを作成（5分）

1. **https://api.slack.com/apps** にアクセス

2. **"Create New App"** → **"From scratch"** を選択

3. **App名と対象ワークスペースを設定**
   - App Name: `採用選考支援Bot` など
   - Workspace: あなたのワークスペース

4. **Socket Modeを有効化**
   - 左メニュー → "Socket Mode"
   - "Enable Socket Mode" をON
   - Token Name: `MyAppToken` など
   - Scope: `connections:write` を選択
   - **🔑 xapp-で始まるトークンをコピー** → メモ帳に保存

5. **Bot Token Scopesを追加**
   - 左メニュー → "OAuth & Permissions"
   - "Scopes" → "Bot Token Scopes" に以下を追加:
     - `app_mentions:read`
     - `chat:write`
     - `files:read`
     - `files:write`

6. **ワークスペースにインストール**
   - 同じページの上部 → "Install to Workspace" をクリック
   - **🔑 xoxb-で始まるBot User OAuth Tokenをコピー** → メモ帳に保存

7. **イベントサブスクリプションを有効化**
   - 左メニュー → "Event Subscriptions"
   - "Enable Events" をON
   - "Subscribe to bot events" に以下を追加:
     - `app_mention`
     - `file_shared`
     - `message.channels`
   - "Save Changes" をクリック

### ステップ2: プロジェクトのセットアップ（2分）

1. **setup.bat をダブルクリック**
   ```
   C:\Users\nnkre\recruitment-slack-agent\setup.bat
   ```

   これにより以下が自動で実行されます：
   - Python バージョン確認
   - 仮想環境の作成
   - 依存関係のインストール
   - .env ファイルの作成

### ステップ3: トークンを設定（1分）

1. **backend\.env** ファイルをメモ帳で開く

2. 以下の行を編集（ステップ1でコピーしたトークンを貼り付け）:

```env
SLACK_BOT_TOKEN=xoxb-あなたのボットトークン
SLACK_APP_TOKEN=xapp-あなたのアプリトークン
```

3. 保存して閉じる

### ステップ4: ボットを起動（1分）

1. **start.bat をダブルクリック**
   ```
   C:\Users\nnkre\recruitment-slack-agent\start.bat
   ```

2. 以下のメッセージが表示されれば成功:
   ```
   ✅ 採用選考支援Slackボット（シンプル版）を起動しています...
   📋 ファイル受付機能が有効です
   🔌 Slackに接続中...
   ⚡️ Bolt app is running!
   ```

## ✅ 動作確認

### 1. Slackチャンネルにボットを招待

1. Slackで採用選考用のチャンネルを作成（例: `#test-bot`）
2. チャンネルで `/invite @あなたのボット名` を実行

### 2. ボットとやり取り

1. **ヘルプを表示**
   ```
   @あなたのボット名 help
   ```

2. **ステータス確認**
   ```
   @あなたのボット名 status
   ```

3. **PDFをアップロード**
   - チャンネルにPDFファイルをドラッグ&ドロップ
   - ボットが受付確認メッセージを返します

## 🎯 AI機能を有効にする（オプション）

AI評価機能を使いたい場合:

### 1. Gemini API Keyを取得

1. **https://makersuite.google.com/app/apikey** にアクセス
2. "Create API Key" をクリック
3. APIキーをコピー

### 2. .env に追加

```env
GEMINI_API_KEY=あなたのGemini APIキー
```

### 3. フル版で起動

**start_full.bat** をダブルクリック（初回は依存関係の追加インストールが実行されます）

## 🛑 ボットを停止

コマンドプロンプト画面で `Ctrl + C` を押す

## 📁 ファイル構成

```
recruitment-slack-agent/
├── setup.bat              ← 初回セットアップ用
├── start.bat              ← シンプル版起動（AI機能なし）
├── start_full.bat         ← フル版起動（AI機能あり）
├── backend/
│   ├── .env               ← トークン設定ファイル
│   └── app/
│       ├── main_simple.py ← シンプル版
│       └── main.py        ← フル版
└── README.md
```

## 🐛 トラブルシューティング

### ボットが起動しない

**エラー: 環境変数が設定されていません**
→ `backend\.env` を編集して、実際のトークンを設定

**エラー: Pythonがインストールされていません**
→ https://www.python.org/downloads/ からPython 3.9以上をインストール

### ボットが反応しない

1. ボットがチャンネルに招待されているか確認
2. コマンドプロンプトにエラーメッセージが表示されていないか確認
3. Slack App管理画面でイベントサブスクリプションが有効か確認

### PDFファイルが処理されない

- シンプル版では受付確認のみです
- AI評価を行うには `start_full.bat` でフル版を起動してください

## 💡 ヒント

- ボットを常時起動させたい場合は、Renderなどのクラウドサービスへのデプロイを検討してください（DEPLOY.md参照）
- 開発中は `start.bat`（シンプル版）で動作確認し、AI機能のテストは `start_full.bat` で行うと効率的です

## 📞 サポート

問題が発生した場合は、コマンドプロンプトのエラーメッセージを確認してください。
