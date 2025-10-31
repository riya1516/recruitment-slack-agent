"""
Recruitment AI Agent - Slack Bot
採用選考支援Slackボット
"""

import os
import json
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from services.evaluator import DocumentEvaluator
from database import SessionLocal
from models.database import Candidate, Evaluation, SelectionStage, JobPosting, CandidateStage, CandidateStatus

# 環境変数の読み込み
load_dotenv()

# Slack Appの初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 評価サービスの初期化
evaluator = DocumentEvaluator()


@app.command("/kaka")
def handle_kaka_command(ack, say, command):
    """
    /kaka スラッシュコマンドの処理
    募集要項と使い方を表示
    """
    ack()  # コマンドを受信したことを確認

    user_id = command.get("user_id")

    # 募集要項を取得
    job_info = evaluator.job_requirements

    message = f"""<@{user_id}> こんにちは！採用選考支援AIボットです。

**Web管理画面にアクセス:**
http://localhost:5175/
↑ブラウザで開いて、募集要項や選考者を管理できます

━━━━━━━━━━━━━━━━━━━━━━━━━━

**現在の募集要項**

職種: {job_info.get('job_title', '未設定')}
部署: {job_info.get('department', '未設定')}
雇用形態: {job_info.get('employment_type', '未設定')}

**Slackでの使い方:**
1. このチャンネルに候補者の履歴書・職務経歴書（PDF）をアップロード
2. AIが自動的に以下の観点で評価します:
   • 技術スキル
   • 経験の質
   • 文化適合性
   • 成長可能性
3. 約30秒〜1分で詳細な評価レポートが返ります

**Web管理画面でできること:**
• 募集要項の作成・編集（複数保持可能）
• 選考者の登録・検索・管理
• 評価基準のカスタマイズ
• 選考段階の設定

**コマンド:**
• `/kaka` - このヘルプを表示
• `@bot help` - 詳細ヘルプ
• `@bot 募集要項` - 募集要項の詳細を表示

それでは、PDFファイルをアップロードするか、Web管理画面にアクセスしてください！
"""

    say(message)


@app.command("/settings")
def handle_settings_command(ack, say, command):
    """
    /settings スラッシュコマンドの処理
    Webアプリケーションへのリンクを表示
    """
    ack()  # コマンドを受信したことを確認

    user_id = command.get("user_id")

    message = f"""<@{user_id}> 採用管理Webアプリケーション

**Webアプリケーションにアクセス:**
http://localhost:5175/

**利用可能な機能:**
• 募集要項の作成・管理
• 選考者の登録・検索
• 評価基準の設定
• AI質問生成（近日公開）

ブラウザでアクセスして、採用管理を始めましょう！
"""

    say(message)


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
2. ファイルをアップロードする際、コメント欄に候補者名を記入してください（例: 「田中太郎さんの履歴書」）
3. AIが自動的にPDFを解析し、評価結果を返します

**評価内容:**
• 技術スキル（必須・優遇スキルとの合致度）
• 経験の質（プロジェクト経験、成果）
• 文化適合性（企業価値観との一致）
• 成長可能性（学習意欲、適応力）

**コマンド:**
• `@bot help` - このヘルプを表示
• `@bot 募集要項` - 現在の募集要項を表示

何か問題があれば、開発チームにお問い合わせください。
        """
        say(help_message)
        return

    # 募集要項を表示
    if "募集要項" in text:
        job_info = evaluator.job_requirements
        message = f"""
📢 **現在の募集要項**

**職種:** {job_info.get('job_title', '未設定')}
**部署:** {job_info.get('department', '未設定')}
**雇用形態:** {job_info.get('employment_type', '未設定')}

**必須スキル:**
{_format_list(job_info.get('required_skills', []))}

**優遇スキル:**
{_format_list(job_info.get('preferred_skills', []))}

**求める人物像:**
{_format_list(job_info.get('desired_personality', []))}
        """
        say(message)
        return

    # デフォルトのメンション応答
    say(f"<@{user}> こんにちは！PDFファイルをアップロードすると、自動的に書類選考の評価を行います。\n詳しくは `@bot help` と入力してください。")


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
        file_url = file_data.get("url_private", "")

        # PDFファイルのみ処理
        if "pdf" not in file_type.lower() and not file_name.lower().endswith(".pdf"):
            say(f"<@{user_id}> PDFファイルのみ対応しています。アップロードされたファイル: {file_name}")
            return

        # 処理開始メッセージ
        say(f"<@{user_id}> 📄 `{file_name}` を受け付けました。評価を開始します...\n⏳ 少々お待ちください（通常30秒～1分程度かかります）")

        # ファイルをダウンロード
        headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
        response = requests.get(file_url, headers=headers)

        if response.status_code != 200:
            say(f"❌ ファイルのダウンロードに失敗しました。もう一度お試しください。")
            return

        pdf_bytes = response.content

        # 候補者名を推定（ファイル名から）
        candidate_name = file_name.replace(".pdf", "").replace("_", " ")

        # 評価を実行
        evaluation_result = evaluator.evaluate_from_pdf_bytes(
            pdf_bytes=pdf_bytes,
            candidate_name=candidate_name
        )

        # データベースに保存
        try:
            candidate_id, candidate_number = _save_candidate_to_db(candidate_name, evaluation_result)
            print(f"[INFO] 候補者をDBに保存しました: {candidate_number}")
        except Exception as db_error:
            print(f"[WARNING] DB保存に失敗しましたが、評価結果は返信します: {str(db_error)}")
            candidate_number = "未割当"

        # 評価結果をフォーマット
        formatted_result = evaluator.format_evaluation_result(evaluation_result)

        # 結果を送信
        say(f"<@{user_id}> ✅ 評価完了\n**候補者番号**: `{candidate_number}`\n\n```\n{formatted_result}\n```\n\nWeb管理画面で詳細を確認: http://localhost:5175/candidates")

        # JSON形式でも送信（詳細確認用）
        json_str = json.dumps(
            evaluation_result,
            ensure_ascii=False,
            indent=2
        )

        # JSONが長すぎる場合は、ファイルとしてアップロード
        if len(json_str) > 3000:
            client.files_upload_v2(
                channel=event.get("channel_id"),
                content=json_str,
                filename=f"evaluation_{candidate_number}_{file_id}.json",
                title=f"詳細評価結果 - {candidate_name} ({candidate_number})",
                initial_comment=f"<@{user_id}> 詳細な評価結果をJSONファイルで添付します。"
            )
        else:
            say(f"<@{user_id}> 📊 詳細評価結果（JSON）:\n```json\n{json_str}\n```")

    except Exception as e:
        error_message = f"❌ 評価中にエラーが発生しました: {str(e)}\n\n開発チームに報告してください。"
        say(f"<@{user_id}> {error_message}")
        print(f"Error processing file: {str(e)}")


def _format_list(items):
    """リストを整形"""
    if not items:
        return "• （設定なし）"
    return "\n".join([f"• {item}" for item in items])


def _generate_candidate_number(db):
    """候補者番号を生成"""
    today = datetime.now()
    prefix = f"C{today.year}{today.month:02d}"

    # 今月の最新番号を取得
    latest = db.query(Candidate).filter(
        Candidate.candidate_number.like(f"{prefix}%")
    ).order_by(Candidate.candidate_number.desc()).first()

    if latest:
        # 既存の番号から連番を取得してインクリメント
        last_num = int(latest.candidate_number[-4:])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


def _save_candidate_to_db(candidate_name, evaluation_result, job_posting_id=None):
    """候補者と評価結果をデータベースに保存"""
    db = SessionLocal()
    try:
        # アクティブな募集要項を取得（指定がない場合は最初のもの）
        if not job_posting_id:
            job_posting = db.query(JobPosting).filter(JobPosting.is_active == True).first()
            if not job_posting:
                # アクティブな募集要項がない場合、最初のものを使用
                job_posting = db.query(JobPosting).first()
            if job_posting:
                job_posting_id = job_posting.id

        # 書類選考の段階を取得
        document_stage = db.query(SelectionStage).filter(
            SelectionStage.job_posting_id == job_posting_id,
            SelectionStage.stage_order == 1
        ).first()

        # 候補者を作成
        candidate_number = _generate_candidate_number(db)
        candidate = Candidate(
            name=candidate_name,
            candidate_number=candidate_number,
            job_posting_id=job_posting_id,
            current_stage_id=document_stage.id if document_stage else None,
            overall_status=CandidateStatus.IN_PROGRESS,
            tags=[],
            notes=""
        )
        db.add(candidate)
        db.flush()  # IDを取得するため

        # 評価結果を保存
        if document_stage:
            # CandidateStageレコードを作成
            candidate_stage = CandidateStage(
                candidate_id=candidate.id,
                stage_id=document_stage.id,
                status="完了",
                notes=""
            )
            db.add(candidate_stage)
            db.flush()

            # 評価データを保存
            eval_data = evaluation_result.get("evaluation_format", {})
            evaluation = Evaluation(
                candidate_id=candidate.id,
                stage_id=document_stage.id,
                evaluator_name="AI評価システム",
                scores=eval_data.get("evaluation_items", {}),
                comments=eval_data.get("overall_comment", ""),
                strengths=eval_data.get("strengths", []),
                concerns=eval_data.get("concerns", []),
                recommendation=eval_data.get("recommendation", ""),
                raw_data=evaluation_result
            )
            db.add(evaluation)

        db.commit()
        return candidate.id, candidate_number

    except Exception as e:
        db.rollback()
        print(f"[ERROR] データベース保存エラー: {str(e)}")
        raise
    finally:
        db.close()


@app.event("message")
def handle_message_events(body, logger):
    """メッセージイベントをログに記録"""
    logger.debug(body)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """ヘルスチェック用のHTTPハンドラー"""

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'service': 'recruitment-slack-bot'
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """ログ出力を抑制"""
        pass


def start_health_check_server():
    """ヘルスチェック用HTTPサーバーを起動"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"[INFO] Health check server started on port {port}")
    server.serve_forever()


def main():
    """メイン関数"""
    # 環境変数チェック
    required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"[ERROR] 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        print("[WARNING] .envファイルを確認してください。")
        return

    print("[OK] 採用選考支援Slackボット（AI機能あり）を起動しています...")
    print("[INFO] 書類選考支援機能が有効です")

    # ヘルスチェック用HTTPサーバーを別スレッドで起動
    health_thread = Thread(target=start_health_check_server, daemon=True)
    health_thread.start()

    print("[INFO] Slackに接続中...")

    # Socket Modeで起動
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()


if __name__ == "__main__":
    main()
