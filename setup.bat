@echo off
echo ========================================
echo 採用選考支援 Slack Bot - セットアップ
echo ========================================
echo.

REM 現在のディレクトリを確認
cd /d %~dp0

echo [1/4] Python のバージョンを確認中...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Pythonがインストールされていません。
    echo Python 3.9以上をインストールしてください。
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] 仮想環境を作成中...
cd backend
if exist venv (
    echo 仮想環境は既に存在します。
) else (
    python -m venv venv
    echo ✓ 仮想環境を作成しました
)
echo.

echo [3/4] 依存関係をインストール中...
call venv\Scripts\activate.bat
pip install -r requirements_simple.txt
echo ✓ 依存関係をインストールしました
echo.

echo [4/4] 環境設定ファイルを確認中...
if exist .env (
    echo .envファイルは既に存在します。
) else (
    copy .env.example .env
    echo ✓ .envファイルを作成しました
    echo.
    echo [重要] .envファイルを編集して、以下のトークンを設定してください:
    echo   1. SLACK_BOT_TOKEN
    echo   2. SLACK_APP_TOKEN
    echo.
    echo トークンの取得方法はREADME.mdを参照してください。
)
echo.

echo ========================================
echo セットアップが完了しました！
echo ========================================
echo.
echo 次のステップ:
echo 1. backend\.env を編集してSlackトークンを設定
echo 2. start.bat をダブルクリックしてボットを起動
echo.
echo AI機能を使う場合:
echo 1. .envにGEMINI_API_KEYを追加
echo 2. start_full.bat を実行
echo.
pause
