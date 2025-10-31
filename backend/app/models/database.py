"""
Database models for recruitment management system
採用管理システムのデータベースモデル
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Float, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class SelectionStageType(enum.Enum):
    """選考段階の種類"""
    DOCUMENT_SCREENING = "書類選考"
    FIRST_INTERVIEW = "一次面接"
    SECOND_INTERVIEW = "二次面接"
    FINAL_INTERVIEW = "最終面接"
    OFFER = "内定"
    CUSTOM = "カスタム"


class CandidateStatus(enum.Enum):
    """選考者のステータス"""
    IN_PROGRESS = "選考中"
    PASSED = "合格"
    FAILED = "不合格"
    PENDING = "保留"
    WITHDRAWN = "辞退"


# ========================================
# 募集要項関連
# ========================================

class JobPosting(Base):
    """募集要項テーブル"""
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    department = Column(String(255))
    employment_type = Column(String(100))
    description = Column(Text)
    requirements = Column(JSON)  # 必須スキル・条件
    preferred_skills = Column(JSON)  # 優遇スキル
    company_values = Column(JSON)  # 企業価値観

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="job_posting")
    selection_stages = relationship("SelectionStage", back_populates="job_posting")
    candidates = relationship("Candidate", back_populates="job_posting")


class EvaluationCriteria(Base):
    """評価基準テーブル"""
    __tablename__ = "evaluation_criteria"

    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))

    # 評価項目
    category = Column(String(100), nullable=False)  # 技術スキル、経験の質、etc.
    weight = Column(Float, default=1.0)  # 重み付け
    description = Column(Text)
    evaluation_points = Column(JSON)  # 評価ポイントのリスト

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    job_posting = relationship("JobPosting", back_populates="evaluation_criteria")


# ========================================
# 選考段階関連
# ========================================

class SelectionStage(Base):
    """選考段階テーブル"""
    __tablename__ = "selection_stages"

    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))

    stage_order = Column(Integer, nullable=False)  # 段階の順序
    stage_name = Column(String(255), nullable=False)
    stage_type = Column(SQLEnum(SelectionStageType), default=SelectionStageType.CUSTOM)
    description = Column(Text)

    # 段階別設定
    evaluation_focus = Column(JSON)  # この段階で重視する評価項目
    required_documents = Column(JSON)  # 必要書類

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    job_posting = relationship("JobPosting", back_populates="selection_stages")
    candidate_stages = relationship("CandidateStage", back_populates="selection_stage")
    ai_questions = relationship("AIQuestion", back_populates="selection_stage")


# ========================================
# 選考者関連
# ========================================

class Candidate(Base):
    """選考者テーブル"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))

    # 基本情報
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    candidate_number = Column(String(50), unique=True, index=True)  # 候補者番号

    # 応募情報
    resume_url = Column(String(500))  # 履歴書のURL
    resume_text = Column(Text)  # 履歴書のテキスト（OCR結果）
    portfolio_url = Column(String(500))

    # ステータス
    current_stage_id = Column(Integer, ForeignKey("selection_stages.id"), nullable=True)
    overall_status = Column(SQLEnum(CandidateStatus), default=CandidateStatus.IN_PROGRESS)

    # カテゴリ・タグ
    tags = Column(JSON)  # カテゴライズ用タグ
    notes = Column(Text)  # メモ

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    job_posting = relationship("JobPosting", back_populates="candidates")
    candidate_stages = relationship("CandidateStage", back_populates="candidate")
    evaluations = relationship("Evaluation", back_populates="candidate")


class CandidateStage(Base):
    """選考者の段階別情報テーブル"""
    __tablename__ = "candidate_stages"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    selection_stage_id = Column(Integer, ForeignKey("selection_stages.id"))

    status = Column(SQLEnum(CandidateStatus), default=CandidateStatus.IN_PROGRESS)
    interview_date = Column(DateTime, nullable=True)
    interview_notes = Column(Text)  # 面接メモ

    # AI生成サマリー
    summary = Column(Text)  # 要点サマリー
    strengths = Column(JSON)  # 強み
    concerns = Column(JSON)  # 懸念点
    characteristics = Column(JSON)  # 特徴

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    candidate = relationship("Candidate", back_populates="candidate_stages")
    selection_stage = relationship("SelectionStage", back_populates="candidate_stages")


# ========================================
# 評価関連
# ========================================

class Evaluation(Base):
    """評価テーブル"""
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    criteria_id = Column(Integer, ForeignKey("evaluation_criteria.id"))
    stage_id = Column(Integer, ForeignKey("selection_stages.id"))

    # 評価内容
    score = Column(Float)  # スコア（任意）
    rating = Column(String(50))  # 評価レベル（例: 優、良、可、不可）
    comments = Column(Text)
    evidence = Column(JSON)  # 評価の根拠となる情報

    # メタ情報
    evaluated_by = Column(String(255))  # 評価者
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    candidate = relationship("Candidate", back_populates="evaluations")


# ========================================
# AI質問生成関連
# ========================================

class AIQuestion(Base):
    """AI生成質問テーブル"""
    __tablename__ = "ai_questions"

    id = Column(Integer, primary_key=True, index=True)
    selection_stage_id = Column(Integer, ForeignKey("selection_stages.id"))

    question = Column(Text, nullable=False)
    category = Column(String(100))  # 質問のカテゴリ
    purpose = Column(Text)  # 質問の目的

    # 生成情報
    generated_by = Column(String(50), default="ai")  # ai or manual
    generation_prompt = Column(Text)  # 生成時のプロンプト

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    selection_stage = relationship("SelectionStage", back_populates="ai_questions")


# ========================================
# Google Drive連携
# ========================================

class GoogleDriveFile(Base):
    """Google Driveファイル管理テーブル"""
    __tablename__ = "google_drive_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(255), unique=True, nullable=False)  # Google Drive File ID
    file_name = Column(String(500))
    file_type = Column(String(100))  # pdf, docx, xlsx, etc.

    # 関連付け
    related_type = Column(String(50))  # candidate, job_posting, etc.
    related_id = Column(Integer)

    # メタデータ
    drive_url = Column(String(1000))
    file_size = Column(Integer)
    mime_type = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
