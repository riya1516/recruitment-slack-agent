"""
Database configuration and session management
データベース設定とセッション管理
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# データベースURL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./recruitment.db"  # デフォルトはSQLite
)

# RenderのPostgreSQL URLは postgres:// で始まるが、SQLAlchemyは postgresql:// を期待する
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # SQLログを表示したい場合はTrue
)

# セッションローカルの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseのインポート
from models.database import Base


def get_db() -> Session:
    """
    データベースセッションを取得する依存関係

    Yields:
        Session: データベースセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    データベースの初期化
    全テーブルを作成
    """
    Base.metadata.create_all(bind=engine)
    print("[INFO] Database tables created successfully")


def reset_db():
    """
    データベースをリセット（開発用）
    全テーブルを削除して再作成
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[WARNING] Database has been reset")
