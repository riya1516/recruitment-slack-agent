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


@app.get("/api/v1/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """システム全体の統計情報を取得"""
    from models.database import Candidate, JobPosting, Evaluation, CandidateStatus
    from sqlalchemy import func

    # 総数
    total_candidates = db.query(Candidate).count()
    total_job_postings = db.query(JobPosting).count()
    total_evaluations = db.query(Evaluation).count()
    active_job_postings = db.query(JobPosting).filter(JobPosting.is_active == True).count()

    # ステータス別の候補者数
    status_counts = db.query(
        Candidate.overall_status,
        func.count(Candidate.id)
    ).group_by(Candidate.overall_status).all()

    status_breakdown = {
        "選考中": 0,
        "合格": 0,
        "不合格": 0,
        "保留": 0
    }

    for status, count in status_counts:
        if status:
            status_breakdown[status.value] = count

    # 最近の候補者（直近5件）
    recent_candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).limit(5).all()

    return {
        "total_candidates": total_candidates,
        "total_job_postings": total_job_postings,
        "active_job_postings": active_job_postings,
        "total_evaluations": total_evaluations,
        "status_breakdown": status_breakdown,
        "recent_candidates": [
            {
                "id": c.id,
                "name": c.name,
                "candidate_number": c.candidate_number,
                "overall_status": c.overall_status.value if c.overall_status else None,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in recent_candidates
        ]
    }


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
