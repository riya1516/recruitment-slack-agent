@echo off
echo ========================================
echo 採用選考支援 Slack Bot (AI機能あり)
echo ========================================
echo.

cd backend

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM .envファイルの確認
if not exist .env (
    echo [エラー] .envファイルが見つかりません。
    echo .env.exampleをコピーして.envを作成し、必要なトークンを設定してください。
    echo.
    pause
    exit /b 1
)

REM トークンの確認
findstr /C:"your-gemini-api-key-here" .env >nul
if %errorlevel% equ 0 (
    echo [警告] GEMINI_API_KEYが設定されていません。
    echo .envファイルを編集して、Gemini API Keyを設定してください。
    echo AI機能なしで起動する場合は、start.bat を使用してください。
    echo.
    pause
    exit /b 1
)

echo ✓ 環境設定を確認しました
echo.

REM フル版の依存関係をインストール（初回のみ）
if not exist venv\Lib\site-packages\google (
    echo フル版の依存関係をインストールしています...
    pip install -r requirements.txt
    echo.
)

echo ボットを起動しています...
echo フル版（AI機能あり）で起動します
echo.
echo 停止する場合は Ctrl+C を押してください
echo ========================================
echo.

REM フル版を起動
python app\main.py

pause
