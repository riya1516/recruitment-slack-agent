# デプロイガイド（クイックスタート）

## 📦 簡単デプロイ - 3ステップ

### ステップ1: Slack Appを作成

1. https://api.slack.com/apps で新規App作成
2. 必要な権限を設定:
   - `app_mentions:read`
   - `chat:write`
   - `files:read`
   - `files:write`
3. Socket Modeを有効化し、App-Level Tokenを生成
4. イベントサブスクリプションを有効化:
   - `app_mention`
   - `file_shared`
   - `message.channels`

### ステップ2: GitHubにプッシュ

```bash
cd recruitment-slack-agent

git init
git add .
git commit -m "Initial commit"

# GitHubで新規リポジトリ作成後
git remote add origin https://github.com/your-username/recruitment-slack-agent.git
git branch -M main
git push -u origin main
```

### ステップ3: Renderでデプロイ

1. **https://render.com** にアクセス、GitHubでサインアップ

2. **New → Background Worker**

3. **設定:**
   - Repository: `recruitment-slack-agent`
   - Name: `recruitment-slack-bot`
   - Build Command: `pip install -r backend/requirements_simple.txt`
   - Start Command: `python backend/app/main_simple.py`

4. **環境変数:**
   - `SLACK_BOT_TOKEN`: `xoxb-...` (Slack OAuth & Permissionsから)
   - `SLACK_APP_TOKEN`: `xapp-...` (Slack Basic Informationから)

5. **Create Background Worker** をクリック

## ✅ 動作確認

1. Renderのログで "✅ 採用選考支援Slackボット（シンプル版）を起動しています..." を確認
2. Slackチャンネルにボットを招待: `/invite @YourBotName`
3. メンションしてテスト: `@YourBotName help`
4. PDFファイルをアップロードして受付確認

## 🚀 AI機能の追加（後日）

1. Renderの環境変数に追加:
   - `GEMINI_API_KEY`: Google Gemini APIキー
2. Start Commandを変更: `python backend/app/main.py`
3. Build Commandを変更: `pip install -r backend/requirements.txt`
4. Manual Deploy → "Deploy latest commit"

## 💡 ヒント

- **無料プラン**: 15分アイドルでスリープ（Socket Modeには不向き）
- **有料プラン**: $7/月〜、24時間稼働
- **ローカルテスト**: `python backend/app/main_simple.py` で起動確認

## 🐛 トラブルシューティング

### ボットが反応しない
- Renderのログを確認
- 環境変数が正しく設定されているか確認
- Slackのイベントサブスクリプションが有効か確認

### デプロイが失敗する
- `requirements_simple.txt` が存在するか確認
- Pythonバージョンが3.9以上か確認
- Renderのビルドログを確認

## 📞 サポート

問題が発生した場合は、Renderのログとエラーメッセージを確認してください。
