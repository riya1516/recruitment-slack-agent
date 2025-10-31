"""
FastAPI Main Application
採用管理システム Web API
"""

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db

# FastAPIアプリケーション
app = FastAPI(
    title="Recruitment Management API",
    description="採用選考支援システムのWeb API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# スタートアップイベント
# ========================================

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    print("[INFO] Starting Recruitment Management API...")
    init_db()
    print("[INFO] API is ready!")


# ========================================
# ヘルスチェック
# ========================================

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Recruitment Management API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


# ========================================
# APIルーターのインポート
# ========================================

from routers import job_postings, candidates, questions

app.include_router(job_postings.router, prefix="/api/v1/job-postings", tags=["募集要項"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["選考者"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["AI質問生成"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
