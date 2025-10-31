# 採用選考支援システム (Recruitment Management System)

Slack連携、AI評価、Web管理画面を備えた総合的な採用選考支援システムです。

## 機能

- **Slack Bot**: PDFアップロードで自動AI評価・データベース保存
- **Web管理画面**: 候補者・募集要項の管理
- **AI質問生成**: 選考段階別に30問の面接質問を自動生成
- **選考段階管理**: ステータス更新・次段階への遷移
- **CSV出力**: 候補者一覧・評価履歴・質問のエクスポート

## 技術スタック

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL (本番) / SQLite (開発)
- Slack Bolt
- Google Gemini API

### Frontend
- React 18
- Vite
- Material-UI
- React Router
- Axios

## ローカル開発

### 必要な環境
- Python 3.11+
- Node.js 18+
- npm

### セットアップ

1. **リポジトリのクローン**
```bash
git clone https://github.com/riya1516/recruitment-slack-agent.git
cd recruitment-slack-agent
```

2. **バックエンドのセットアップ**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **環境変数の設定**
`backend/.env` ファイルを作成:
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///./recruitment.db
```

4. **フロントエンドのセットアップ**
```bash
cd frontend
npm install
```

5. **起動**

バックエンドAPI:
```bash
cd backend/app
python api_main.py
```

Slack Bot:
```bash
cd backend/app
python main.py
```

フロントエンド:
```bash
cd frontend
npm run dev
```

Web管理画面: http://localhost:5173

## Renderへのデプロイ

### 前提条件
- GitHubアカウント
- Renderアカウント (無料)
- Slack App (Bot Token, App Token)
- Google Gemini API Key

### デプロイ手順

1. **GitHubにプッシュ**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/riya1516/recruitment-slack-agent.git
git branch -M main
git push -u origin main
```

2. **Renderでサービス作成**

Render Dashboard (https://dashboard.render.com/) にアクセス:

- **New > Blueprint** をクリック
- GitHubリポジトリを接続
- `recruitment-slack-agent` を選択
- `render.yaml` が自動検出される
- **Apply** をクリック

4つのサービスが自動作成されます:
- `recruitment-db` (PostgreSQL)
- `recruitment-api` (FastAPI)
- `recruitment-slack-bot` (Worker)
- `recruitment-frontend` (Static Site)

3. **環境変数の設定**

各サービスで以下の環境変数を設定:

**recruitment-api**:
- `GEMINI_API_KEY`: あなたのGemini API Key

**recruitment-slack-bot**:
- `SLACK_BOT_TOKEN`: xoxb-で始まるBot Token
- `SLACK_APP_TOKEN`: xapp-で始まるApp Token
- `GEMINI_API_KEY`: あなたのGemini API Key

**recruitment-frontend**:
- `VITE_API_URL`: `https://recruitment-api.onrender.com/api/v1` (あなたのAPIのURL)

4. **CORS設定の更新**

デプロイ後、`backend/app/api_main.py` のCORS設定を本番URLに更新:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://recruitment-frontend.onrender.com",  # あなたのフロントエンドURL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

変更後、GitHubにプッシュすると自動的に再デプロイされます。

5. **Slack Appの設定**

Slack App設定 (https://api.slack.com/apps) で:
- **Socket Mode** を有効化
- **OAuth & Permissions** で必要なスコープを追加:
  - `chat:write`
  - `files:read`
  - `commands`

6. **デプロイ完了**

すべてのサービスが正常に起動したら:
- Web管理画面: `https://recruitment-frontend.onrender.com`
- API: `https://recruitment-api.onrender.com`
- Slack Botが稼働中

## 使い方

1. 募集要項を作成（職種、必須スキル、評価基準を設定）
2. Slackで候補者のPDFをアップロード → AIが自動評価
3. Web管理画面で候補者を確認 → 詳細ページでAI質問生成
4. 面接実施 → 評価入力 → 次段階へ進める
5. 必要に応じてCSVエクスポート（候補者一覧・評価履歴・質問）

## プロジェクト構造

```
recruitment-slack-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                    # Slack Bot
│   │   ├── api_main.py               # FastAPI App
│   │   ├── database.py               # Database config
│   │   ├── models/
│   │   │   └── database.py           # SQLAlchemy models
│   │   ├── routers/
│   │   │   ├── job_postings.py      # Job posting endpoints
│   │   │   ├── candidates.py        # Candidate endpoints
│   │   │   └── questions.py         # AI question endpoints
│   │   └── services/
│   │       ├── gemini_service.py    # Gemini API
│   │       ├── pdf_parser.py        # PDF parsing
│   │       ├── evaluator.py         # AI evaluation
│   │       └── question_generator.py # AI questions
│   └── requirements.txt              # Python deps
├── frontend/
│   ├── src/
│   │   ├── pages/                   # React pages
│   │   ├── components/              # React components
│   │   └── config.js               # App config
│   ├── package.json
│   └── vite.config.js
├── render.yaml                       # Render deployment config
└── README.md
```

## トラブルシューティング

### Renderでビルドが失敗する
- Python バージョンを確認 (3.11推奨)
- requirements.txt の依存関係を確認
- ログで詳細なエラーを確認

### Slack Botが応答しない
- 環境変数 `SLACK_BOT_TOKEN` と `SLACK_APP_TOKEN` を確認
- Render Logs で Worker のログを確認
- Socket Modeが有効化されているか確認

### フロントエンドがAPIに接続できない
- `VITE_API_URL` が正しく設定されているか確認
- CORS設定が正しいか確認（フロントエンドのURLが許可されているか）
- ブラウザの開発者ツールでネットワークエラーを確認

### データベース接続エラー
- `DATABASE_URL` が正しく設定されているか確認
- PostgreSQLサービスが正常に起動しているか確認

## 注意事項

- Renderの無料プランは非アクティブ時にスリープします
- 初回アクセス時に起動に30秒～1分程度かかる場合があります
- 本番運用前に十分なテストを行ってください

## ライセンス

MIT
