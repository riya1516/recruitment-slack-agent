"""
Candidates Router
選考者のAPI エンドポイント
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import csv
import io

from database import get_db
from models.database import Candidate, CandidateStatus, Evaluation, CandidateStage, SelectionStage, JobPosting

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class CandidateCreate(BaseModel):
    job_posting_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    candidate_number: str | None = None
    resume_text: str | None = None
    tags: list | None = None
    notes: str | None = None


class CandidateStatusUpdate(BaseModel):
    status: str  # 選考中、合格、不合格、保留


class StageStatusUpdate(BaseModel):
    stage_id: int
    status: str  # 未着手、進行中、完了、スキップ
    notes: str | None = None


class CandidateResponse(BaseModel):
    id: int
    job_posting_id: int
    name: str
    email: str | None
    phone: str | None
    candidate_number: str | None
    overall_status: str
    tags: list | None
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    stage_id: int
    stage_name: str
    evaluator_name: str
    scores: dict
    comments: str | None
    strengths: list
    concerns: list
    recommendation: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class StageProgressResponse(BaseModel):
    stage_id: int
    stage_name: str
    stage_order: int
    status: str
    notes: str | None

    class Config:
        from_attributes = True


class CandidateDetailResponse(BaseModel):
    id: int
    job_posting_id: int
    job_posting_title: str | None
    name: str
    email: str | None
    phone: str | None
    candidate_number: str | None
    overall_status: str
    tags: list | None
    notes: str | None
    created_at: datetime
    evaluations: List[EvaluationResponse]
    stage_progress: List[StageProgressResponse]

    class Config:
        from_attributes = True


# ========================================
# API Endpoints
# ========================================

@router.get("/", response_model=List[CandidateResponse])
def get_candidates(
    job_posting_id: int | None = None,
    status: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    選考者の一覧を取得

    Args:
        job_posting_id: 募集要項IDでフィルタ
        status: ステータスでフィルタ
        search: 名前・メールで検索
        skip: スキップする件数
        limit: 取得する最大件数
        db: データベースセッション

    Returns:
        選考者のリスト
    """
    query = db.query(Candidate)

    if job_posting_id:
        query = query.filter(Candidate.job_posting_id == job_posting_id)

    if status:
        query = query.filter(Candidate.overall_status == status)

    if search:
        query = query.filter(
            (Candidate.name.contains(search)) |
            (Candidate.email.contains(search))
        )

    candidates = query.offset(skip).limit(limit).all()
    return candidates


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    選考者の詳細を取得（評価履歴と選考段階を含む）

    Args:
        candidate_id: 選考者ID
        db: データベースセッション

    Returns:
        選考者の詳細情報
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    # 募集要項のタイトルを取得
    job_posting = db.query(JobPosting).filter(JobPosting.id == candidate.job_posting_id).first()
    job_posting_title = job_posting.title if job_posting else None

    # 評価履歴を取得
    evaluations = db.query(Evaluation).filter(Evaluation.candidate_id == candidate_id).all()
    evaluation_responses = []
    for evaluation in evaluations:
        stage = db.query(SelectionStage).filter(SelectionStage.id == evaluation.stage_id).first()
        evaluation_responses.append(EvaluationResponse(
            id=evaluation.id,
            stage_id=evaluation.stage_id,
            stage_name=stage.stage_name if stage else "不明",
            evaluator_name=evaluation.evaluator_name,
            scores=evaluation.scores or {},
            comments=evaluation.comments,
            strengths=evaluation.strengths or [],
            concerns=evaluation.concerns or [],
            recommendation=evaluation.recommendation,
            created_at=evaluation.created_at
        ))

    # 選考段階の進捗を取得
    candidate_stages = db.query(CandidateStage).filter(
        CandidateStage.candidate_id == candidate_id
    ).all()
    stage_progress = []
    for cs in candidate_stages:
        stage = db.query(SelectionStage).filter(SelectionStage.id == cs.stage_id).first()
        if stage:
            stage_progress.append(StageProgressResponse(
                stage_id=stage.id,
                stage_name=stage.stage_name,
                stage_order=stage.stage_order,
                status=cs.status,
                notes=cs.notes
            ))

    # ソート（stage_orderで）
    stage_progress.sort(key=lambda x: x.stage_order)

    return CandidateDetailResponse(
        id=candidate.id,
        job_posting_id=candidate.job_posting_id,
        job_posting_title=job_posting_title,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        candidate_number=candidate.candidate_number,
        overall_status=candidate.overall_status.value if hasattr(candidate.overall_status, 'value') else str(candidate.overall_status),
        tags=candidate.tags or [],
        notes=candidate.notes,
        created_at=candidate.created_at,
        evaluations=evaluation_responses,
        stage_progress=stage_progress
    )


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    """
    選考者を新規登録

    Args:
        candidate: 選考者データ
        db: データベースセッション

    Returns:
        作成された選考者
    """
    # 候補者番号の自動生成（指定がない場合）
    if not candidate.candidate_number:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        candidate.candidate_number = f"CAND-{timestamp}"

    db_candidate = Candidate(**candidate.model_dump())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return db_candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    """
    選考者情報を更新

    Args:
        candidate_id: 選考者ID
        candidate: 更新データ
        db: データベースセッション

    Returns:
        更新された選考者
    """
    db_candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    for key, value in candidate.model_dump(exclude_unset=True).items():
        setattr(db_candidate, key, value)

    db.commit()
    db.refresh(db_candidate)

    return db_candidate


@router.put("/{candidate_id}/status", response_model=CandidateResponse)
def update_candidate_status(
    candidate_id: int,
    status_update: CandidateStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    候補者の全体ステータスを更新

    Args:
        candidate_id: 候補者ID
        status_update: ステータス更新データ
        db: データベースセッション

    Returns:
        更新された候補者
    """
    db_candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    # ステータスをCandidateStatusに変換
    try:
        new_status = CandidateStatus(status_update.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_update.status}. Valid values: 選考中, 合格, 不合格, 保留"
        )

    db_candidate.overall_status = new_status
    db.commit()
    db.refresh(db_candidate)

    return db_candidate


@router.post("/{candidate_id}/advance-stage")
def advance_candidate_stage(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    候補者を次の選考段階に進める

    Args:
        candidate_id: 候補者ID
        db: データベースセッション

    Returns:
        成功メッセージと新しい段階情報
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    # 現在の段階を取得
    current_stage = db.query(SelectionStage).filter(
        SelectionStage.id == candidate.current_stage_id
    ).first()

    if not current_stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current stage not found"
        )

    # 次の段階を取得
    next_stage = db.query(SelectionStage).filter(
        SelectionStage.job_posting_id == candidate.job_posting_id,
        SelectionStage.stage_order == current_stage.stage_order + 1
    ).first()

    if not next_stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No next stage available. This is the final stage."
        )

    # 現在の段階を「完了」にする
    current_candidate_stage = db.query(CandidateStage).filter(
        CandidateStage.candidate_id == candidate_id,
        CandidateStage.stage_id == current_stage.id
    ).first()

    if current_candidate_stage:
        current_candidate_stage.status = "完了"
    else:
        # レコードが存在しない場合は作成
        current_candidate_stage = CandidateStage(
            candidate_id=candidate_id,
            stage_id=current_stage.id,
            status="完了",
            notes=""
        )
        db.add(current_candidate_stage)

    # 次の段階のレコードを作成
    next_candidate_stage = db.query(CandidateStage).filter(
        CandidateStage.candidate_id == candidate_id,
        CandidateStage.stage_id == next_stage.id
    ).first()

    if not next_candidate_stage:
        next_candidate_stage = CandidateStage(
            candidate_id=candidate_id,
            stage_id=next_stage.id,
            status="進行中",
            notes=""
        )
        db.add(next_candidate_stage)
    else:
        next_candidate_stage.status = "進行中"

    # 候補者の現在段階を更新
    candidate.current_stage_id = next_stage.id

    db.commit()

    return {
        "message": "Candidate advanced to next stage",
        "previous_stage": current_stage.stage_name,
        "current_stage": next_stage.stage_name
    }


@router.put("/{candidate_id}/stage-status")
def update_stage_status(
    candidate_id: int,
    stage_update: StageStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    特定の選考段階のステータスを更新

    Args:
        candidate_id: 候補者ID
        stage_update: 段階ステータス更新データ
        db: データベースセッション

    Returns:
        成功メッセージ
    """
    candidate_stage = db.query(CandidateStage).filter(
        CandidateStage.candidate_id == candidate_id,
        CandidateStage.stage_id == stage_update.stage_id
    ).first()

    if not candidate_stage:
        # レコードが存在しない場合は作成
        candidate_stage = CandidateStage(
            candidate_id=candidate_id,
            stage_id=stage_update.stage_id,
            status=stage_update.status,
            notes=stage_update.notes or ""
        )
        db.add(candidate_stage)
    else:
        candidate_stage.status = stage_update.status
        if stage_update.notes is not None:
            candidate_stage.notes = stage_update.notes

    db.commit()

    return {"message": "Stage status updated successfully"}


@router.get("/export")
def export_candidates_csv(
    job_posting_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    """
    候補者一覧をCSVでエクスポート

    Args:
        job_posting_id: 募集要項IDでフィルタ
        status: ステータスでフィルタ
        db: データベースセッション

    Returns:
        CSVファイル
    """
    query = db.query(Candidate)

    if job_posting_id:
        query = query.filter(Candidate.job_posting_id == job_posting_id)

    if status:
        query = query.filter(Candidate.overall_status == status)

    candidates = query.all()

    # CSVを生成
    output = io.StringIO()
    writer = csv.writer(output)

    # ヘッダー
    writer.writerow([
        "候補者番号",
        "名前",
        "メールアドレス",
        "電話番号",
        "応募職種",
        "現在の段階",
        "全体ステータス",
        "タグ",
        "登録日時",
        "備考"
    ])

    # データ行
    for candidate in candidates:
        # 募集要項タイトルを取得
        job_posting = db.query(JobPosting).filter(JobPosting.id == candidate.job_posting_id).first()
        job_title = job_posting.title if job_posting else ""

        # 現在の段階名を取得
        current_stage = db.query(SelectionStage).filter(
            SelectionStage.id == candidate.current_stage_id
        ).first()
        current_stage_name = current_stage.stage_name if current_stage else ""

        writer.writerow([
            candidate.candidate_number or "",
            candidate.name,
            candidate.email or "",
            candidate.phone or "",
            job_title,
            current_stage_name,
            candidate.overall_status.value if hasattr(candidate.overall_status, 'value') else str(candidate.overall_status),
            ",".join(candidate.tags) if candidate.tags else "",
            candidate.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            candidate.notes or ""
        ])

    # CSVレスポンスを返す
    output.seek(0)
    filename = f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),  # BOM付きUTF-8でExcel対応
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/{candidate_id}/evaluations/export")
def export_candidate_evaluations_csv(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    特定候補者の評価履歴をCSVでエクスポート

    Args:
        candidate_id: 候補者ID
        db: データベースセッション

    Returns:
        CSVファイル
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    # 評価履歴を取得
    evaluations = db.query(Evaluation).filter(
        Evaluation.candidate_id == candidate_id
    ).order_by(Evaluation.created_at.desc()).all()

    # CSVを生成
    output = io.StringIO()
    writer = csv.writer(output)

    # ヘッダー
    writer.writerow([
        "候補者番号",
        "候補者名",
        "選考段階",
        "評価者",
        "総合コメント",
        "強み",
        "懸念点",
        "推薦",
        "評価日時"
    ])

    # データ行
    for evaluation in evaluations:
        stage = db.query(SelectionStage).filter(SelectionStage.id == evaluation.stage_id).first()
        stage_name = stage.stage_name if stage else "不明"

        writer.writerow([
            candidate.candidate_number or "",
            candidate.name,
            stage_name,
            evaluation.evaluator_name,
            evaluation.comments or "",
            " | ".join(evaluation.strengths) if evaluation.strengths else "",
            " | ".join(evaluation.concerns) if evaluation.concerns else "",
            evaluation.recommendation or "",
            evaluation.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    # 詳細なスコアを別シートとして追加（CSVなので別セクション）
    if evaluations:
        writer.writerow([])  # 空行
        writer.writerow(["=== 詳細スコア ==="])
        writer.writerow([])

        for idx, evaluation in enumerate(evaluations, 1):
            stage = db.query(SelectionStage).filter(SelectionStage.id == evaluation.stage_id).first()
            stage_name = stage.stage_name if stage else "不明"

            writer.writerow([f"評価 {idx}: {stage_name} ({evaluation.created_at.strftime('%Y-%m-%d')})"])

            if evaluation.scores:
                writer.writerow(["評価項目", "スコア/コメント"])
                for key, value in evaluation.scores.items():
                    if isinstance(value, dict):
                        value_str = " | ".join([f"{k}: {v}" for k, v in value.items()])
                    else:
                        value_str = str(value)
                    writer.writerow([key, value_str])

            writer.writerow([])  # 空行

    # CSVレスポンスを返す
    output.seek(0)
    filename = f"evaluations_{candidate.candidate_number}_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/import")
async def import_candidates_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    CSVファイルから候補者を一括インポート

    CSVフォーマット:
    - ヘッダー行必須
    - 列: 名前, メールアドレス, 電話番号, 応募職種ID, 備考

    Args:
        file: アップロードされたCSVファイル
        db: データベースセッション

    Returns:
        インポート結果（成功数、失敗数、エラー詳細）
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルのみ対応しています"
        )

    try:
        # ファイル内容を読み込む
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # BOM付きUTF-8対応
        csv_reader = csv.DictReader(io.StringIO(decoded))

        success_count = 0
        error_count = 0
        errors = []
        created_candidates = []

        for row_num, row in enumerate(csv_reader, start=2):  # ヘッダー行を1として、データは2行目から
            try:
                # 必須フィールドのチェック
                name = row.get('名前', '').strip()
                job_posting_id_str = row.get('応募職種ID', '').strip()

                if not name:
                    errors.append(f"行{row_num}: 名前が空です")
                    error_count += 1
                    continue

                if not job_posting_id_str:
                    errors.append(f"行{row_num}: 応募職種IDが空です")
                    error_count += 1
                    continue

                # 応募職種IDを整数に変換
                try:
                    job_posting_id = int(job_posting_id_str)
                except ValueError:
                    errors.append(f"行{row_num}: 応募職種IDが無効です（{job_posting_id_str}）")
                    error_count += 1
                    continue

                # 募集要項の存在確認
                job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
                if not job_posting:
                    errors.append(f"行{row_num}: 応募職種ID {job_posting_id} が見つかりません")
                    error_count += 1
                    continue

                # 候補者番号の自動生成
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                import random
                random_suffix = random.randint(1000, 9999)
                candidate_number = f"CAND-{timestamp}-{random_suffix}"

                # 候補者データを作成
                candidate = Candidate(
                    job_posting_id=job_posting_id,
                    name=name,
                    email=row.get('メールアドレス', '').strip() or None,
                    phone=row.get('電話番号', '').strip() or None,
                    candidate_number=candidate_number,
                    notes=row.get('備考', '').strip() or None,
                    overall_status=CandidateStatus.IN_PROGRESS
                )

                db.add(candidate)
                db.flush()  # IDを取得するため

                created_candidates.append({
                    'id': candidate.id,
                    'name': candidate.name,
                    'candidate_number': candidate.candidate_number
                })

                success_count += 1

            except Exception as e:
                errors.append(f"行{row_num}: {str(e)}")
                error_count += 1
                continue

        # 全てコミット
        if success_count > 0:
            db.commit()

        return {
            "success": True,
            "total_rows": success_count + error_count,
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10],  # 最初の10件のエラーのみ返す
            "created_candidates": created_candidates[:5]  # 最初の5件のみ返す
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSVファイルの処理中にエラーが発生しました: {str(e)}"
        )
