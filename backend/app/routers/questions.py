"""
Questions Router
AI質問生成のAPIエンドポイント
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import csv
import io

from database import get_db
from models.database import AIQuestion, Candidate, SelectionStage, Evaluation
from services.question_generator import QuestionGenerator

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class QuestionGenerateRequest(BaseModel):
    candidate_id: int
    stage_id: int
    num_questions: int = 30


class QuestionResponse(BaseModel):
    id: int
    candidate_id: int
    stage_id: int
    question_text: str
    purpose: str | None
    category: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ========================================
# API Endpoints
# ========================================

@router.post("/generate", response_model=List[QuestionResponse])
def generate_questions(
    request: QuestionGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    AI質問を生成してデータベースに保存

    Args:
        request: 質問生成リクエスト
        db: データベースセッション

    Returns:
        生成された質問のリスト
    """
    # 候補者情報を取得
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {request.candidate_id} not found"
        )

    # 選考段階情報を取得
    stage = db.query(SelectionStage).filter(SelectionStage.id == request.stage_id).first()
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Selection stage with ID {request.stage_id} not found"
        )

    # 評価サマリーを取得（これまでの評価から）
    evaluation = db.query(Evaluation).filter(
        Evaluation.candidate_id == request.candidate_id
    ).order_by(Evaluation.created_at.desc()).first()

    evaluation_summary = None
    if evaluation:
        evaluation_summary = {
            "strengths": evaluation.strengths or [],
            "concerns": evaluation.concerns or []
        }

    # 質問を生成
    generator = QuestionGenerator()
    questions_data = generator.generate_questions(
        candidate_name=candidate.name,
        stage_name=stage.stage_name,
        job_title=stage.job_posting.title if stage.job_posting else "未設定",
        candidate_resume=candidate.resume_text,
        evaluation_summary=evaluation_summary,
        num_questions=request.num_questions
    )

    # データベースに保存
    saved_questions = []
    for q_data in questions_data:
        question = AIQuestion(
            candidate_id=request.candidate_id,
            stage_id=request.stage_id,
            question_text=q_data.get("question", ""),
            purpose=q_data.get("purpose"),
            category=q_data.get("category")
        )
        db.add(question)
        saved_questions.append(question)

    db.commit()

    # IDを取得するためにリフレッシュ
    for q in saved_questions:
        db.refresh(q)

    return saved_questions


@router.get("/candidate/{candidate_id}/stage/{stage_id}", response_model=List[QuestionResponse])
def get_questions(
    candidate_id: int,
    stage_id: int,
    db: Session = Depends(get_db)
):
    """
    特定の候補者・選考段階の質問を取得

    Args:
        candidate_id: 候補者ID
        stage_id: 選考段階ID
        db: データベースセッション

    Returns:
        質問のリスト
    """
    questions = db.query(AIQuestion).filter(
        AIQuestion.candidate_id == candidate_id,
        AIQuestion.stage_id == stage_id
    ).order_by(AIQuestion.created_at.desc()).all()

    return questions


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    質問を削除

    Args:
        question_id: 質問ID
        db: データベースセッション

    Returns:
        成功メッセージ
    """
    question = db.query(AIQuestion).filter(AIQuestion.id == question_id).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )

    db.delete(question)
    db.commit()

    return {"message": "Question deleted successfully"}


@router.get("/candidate/{candidate_id}/stage/{stage_id}/export")
def export_questions_csv(
    candidate_id: int,
    stage_id: int,
    db: Session = Depends(get_db)
):
    """
    質問をCSVでエクスポート

    Args:
        candidate_id: 候補者ID
        stage_id: 選考段階ID
        db: データベースセッション

    Returns:
        CSVファイル
    """
    # 候補者と段階情報を取得
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    stage = db.query(SelectionStage).filter(SelectionStage.id == stage_id).first()

    if not candidate or not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate or stage not found"
        )

    # 質問を取得
    questions = db.query(AIQuestion).filter(
        AIQuestion.candidate_id == candidate_id,
        AIQuestion.stage_id == stage_id
    ).order_by(AIQuestion.created_at.desc()).all()

    # CSVを生成
    output = io.StringIO()
    writer = csv.writer(output)

    # ヘッダー
    writer.writerow(["番号", "質問", "目的", "カテゴリ", "生成日時"])

    # データ行
    for idx, question in enumerate(questions, start=1):
        writer.writerow([
            idx,
            question.question_text,
            question.purpose or "",
            question.category or "",
            question.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    # CSVレスポンスを返す
    output.seek(0)
    filename = f"questions_{candidate.candidate_number}_{stage.stage_name}_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),  # BOM付きUTF-8でExcel対応
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
