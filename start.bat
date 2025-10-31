@echo off
echo ========================================
echo 採用選考支援 Slack Bot
echo ========================================
echo.

cd backend

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM .envファイルの確認
if not exist .env (
    echo [エラー] .envファイルが見つかりません。
    echo .env.exampleをコピーして.envを作成し、Slack トークンを設定してください。
    echo.
    pause
    exit /b 1
)

REM トークンの確認
findstr /C:"xoxb-your-bot-token-here" .env >nul
if %errorlevel% equ 0 (
    echo [警告] SLACK_BOT_TOKENが設定されていません。
    echo .envファイルを編集して、実際のトークンを設定してください。
    echo.
    pause
    exit /b 1
)

echo ✓ 環境設定を確認しました
echo.
echo ボットを起動しています...
echo シンプル版（AI機能なし）で起動します
echo AI機能を使いたい場合は、start_full.bat を使用してください
echo.
echo 停止する場合は Ctrl+C を押してください
echo ========================================
echo.

REM シンプル版を起動
python app\main_simple.py

pause
