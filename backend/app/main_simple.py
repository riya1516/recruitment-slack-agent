"""
Recruitment AI Agent - Slack Bot (Simple Version for Deployment)
採用選考支援Slackボット（AI機能なしのシンプル版）
"""

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 環境変数の読み込み
load_dotenv()

# Slack Appの初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("app_mention")
def handle_app_mention(event, say, client):
    """
    ボットがメンションされた時の処理
    """
    user = event.get("user")
    text = event.get("text", "")

    # ヘルプメッセージを表示
    if "help" in text.lower() or "ヘルプ" in text:
        help_message = """
📋 **採用選考支援AIエージェント**

このボットは書類選考を支援します。

**使い方:**
1. このチャンネルに候補者の履歴書・職務経歴書（PDF）をアップロードしてください
2. ファイルをアップロードする際、コメント欄に候補者名を記入してください
3. ボットが受付確認メッセージを返します

**コマンド:**
• `@bot help` - このヘルプを表示
• `@bot status` - ボットの状態を確認

何か問題があれば、開発チームにお問い合わせください。
        """
        say(help_message)
        return

    # ステータス確認
    if "status" in text.lower():
        say(f"<@{user}> ✅ ボットは正常に動作しています！\n⚠️ AI評価機能は現在準備中です。")
        return

    # デフォルトのメンション応答
    say(f"<@{user}> こんにちは！PDFファイルをアップロードすると、受付確認を行います。\n詳しくは `@bot help` と入力してください。")


@app.event("file_shared")
def handle_file_upload(event, say, client):
    """
    ファイルがアップロードされた時の処理
    """
    file_id = event.get("file_id")
    user_id = event.get("user_id")

    try:
        # ファイル情報を取得
        file_info = client.files_info(file=file_id)
        file_data = file_info.get("file", {})

        file_name = file_data.get("name", "")
        file_type = file_data.get("mimetype", "")

        # PDFファイルのみ処理
        if "pdf" not in file_type.lower() and not file_name.lower().endswith(".pdf"):
            say(f"<@{user_id}> PDFファイルのみ対応しています。アップロードされたファイル: {file_name}")
            return

        # 受付確認メッセージ
        say(f"<@{user_id}> ✅ `{file_name}` を受け付けました！\n\n📝 ファイル情報:\n• ファイル名: {file_name}\n• ファイルID: {file_id}\n\n⚠️ AI評価機能は現在準備中です。近日中に実装予定です。")

    except Exception as e:
        error_message = f"❌ ファイル処理中にエラーが発生しました: {str(e)}"
        say(f"<@{user_id}> {error_message}")
        print(f"Error processing file: {str(e)}")


@app.event("message")
def handle_message_events(body, logger):
    """メッセージイベントをログに記録"""
    logger.debug(body)


def main():
    """メイン関数"""
    # 環境変数チェック
    required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"[ERROR] 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        print("[WARNING] .envファイルを確認してください。")
        return

    print("[OK] 採用選考支援Slackボット（シンプル版）を起動しています...")
    print("[INFO] ファイル受付機能が有効です")
    print("[INFO] AI評価機能は無効です")
    print("[INFO] Slackに接続中...")

    # Socket Modeで起動
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()


if __name__ == "__main__":
    main()
