import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

# 銀行管理用データベース設定
BANK_DATABASE_URL = os.getenv("BANK_DATABASE_URL", "postgresql://puser:ppassword@localhost:5432/portal?client_encoding=utf8")

# 銀行管理用エンジンとセッション
bank_engine = create_engine(
    BANK_DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)
BankSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=bank_engine)

# 銀行管理用Baseクラス
BankBase = declarative_base()

def get_bank_db() -> Generator:
    """銀行管理用データベースセッションを取得"""
    db = BankSessionLocal()
    try:
        yield db
    finally:
        db.close()
