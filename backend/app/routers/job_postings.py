"""
Job Postings Router
募集要項のAPI エンドポイント
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.database import JobPosting, EvaluationCriteria, SelectionStage, SelectionStageType

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class EvaluationCriteriaCreate(BaseModel):
    category: str
    weight: float = 1.0
    description: str | None = None
    evaluation_points: list | None = None


class SelectionStageCreate(BaseModel):
    stage_order: int
    stage_name: str
    stage_type: str = "CUSTOM"
    description: str | None = None
    evaluation_focus: list | None = None


class JobPostingCreate(BaseModel):
    title: str
    department: str | None = None
    employment_type: str | None = None
    description: str | None = None
    requirements: list | None = None
    preferred_skills: list | None = None
    company_values: list | None = None


class JobPostingResponse(BaseModel):
    id: int
    title: str
    department: str | None
    employment_type: str | None
    description: str | None
    requirements: list | None
    preferred_skills: list | None
    company_values: list | None
    is_active: bool

    class Config:
        from_attributes = True


# ========================================
# API Endpoints
# ========================================

@router.get("/", response_model=List[JobPostingResponse])
def get_job_postings(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    募集要項の一覧を取得

    Args:
        skip: スキップする件数
        limit: 取得する最大件数
        active_only: アクティブな募集要項のみ取得
        db: データベースセッション

    Returns:
        募集要項のリスト
    """
    query = db.query(JobPosting)

    if active_only:
        query = query.filter(JobPosting.is_active == True)

    job_postings = query.offset(skip).limit(limit).all()
    return job_postings


@router.get("/{job_posting_id}", response_model=JobPostingResponse)
def get_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db)
):
    """
    募集要項の詳細を取得

    Args:
        job_posting_id: 募集要項ID
        db: データベースセッション

    Returns:
        募集要項の詳細

    Raises:
        HTTPException: 募集要項が見つからない場合
    """
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job posting with ID {job_posting_id} not found"
        )

    return job_posting


@router.post("/", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db)
):
    """
    募集要項を新規作成

    Args:
        job_posting: 募集要項データ
        db: データベースセッション

    Returns:
        作成された募集要項
    """
    db_job_posting = JobPosting(**job_posting.model_dump())
    db.add(db_job_posting)
    db.commit()
    db.refresh(db_job_posting)

    # デフォルトの評価基準を作成
    default_criteria = [
        {"category": "技術スキル", "weight": 1.0, "description": "必須スキル・優遇スキルとの合致度"},
        {"category": "経験の質", "weight": 1.0, "description": "プロジェクト経験の深さ、成果、責任範囲"},
        {"category": "文化適合性", "weight": 1.0, "description": "企業価値観との一致度、コミュニケーションスタイル"},
        {"category": "コミュニケーション能力", "weight": 1.0, "description": "説明力、傾聴力、協調性"},
        {"category": "成長可能性", "weight": 1.0, "description": "学習意欲、スキルの発展軌跡、適応力"},
    ]

    for criteria_data in default_criteria:
        criteria = EvaluationCriteria(
            job_posting_id=db_job_posting.id,
            **criteria_data
        )
        db.add(criteria)

    # デフォルトの選考段階を作成
    default_stages = [
        {"stage_order": 1, "stage_name": "書類選考", "stage_type": "DOCUMENT_SCREENING"},
        {"stage_order": 2, "stage_name": "一次面接", "stage_type": "FIRST_INTERVIEW"},
        {"stage_order": 3, "stage_name": "二次面接", "stage_type": "SECOND_INTERVIEW"},
        {"stage_order": 4, "stage_name": "最終面接", "stage_type": "FINAL_INTERVIEW"},
    ]

    for stage_data in default_stages:
        stage = SelectionStage(
            job_posting_id=db_job_posting.id,
            **stage_data
        )
        db.add(stage)

    db.commit()
    db.refresh(db_job_posting)

    return db_job_posting


@router.put("/{job_posting_id}", response_model=JobPostingResponse)
def update_job_posting(
    job_posting_id: int,
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db)
):
    """
    募集要項を更新

    Args:
        job_posting_id: 募集要項ID
        job_posting: 更新データ
        db: データベースセッション

    Returns:
        更新された募集要項

    Raises:
        HTTPException: 募集要項が見つからない場合
    """
    db_job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not db_job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job posting with ID {job_posting_id} not found"
        )

    for key, value in job_posting.model_dump().items():
        setattr(db_job_posting, key, value)

    db.commit()
    db.refresh(db_job_posting)

    return db_job_posting


@router.delete("/{job_posting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db)
):
    """
    募集要項を削除（論理削除）

    Args:
        job_posting_id: 募集要項ID
        db: データベースセッション

    Raises:
        HTTPException: 募集要項が見つからない場合
    """
    db_job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()

    if not db_job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job posting with ID {job_posting_id} not found"
        )

    db_job_posting.is_active = False
    db.commit()

    return None
