from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from .config import get_bank_db
from ..account.config import get_account_db
from ..account.service import Account
from .models import BankAccount, Transaction

router = APIRouter()

class BankAccountRequest(BaseModel):
    username: str
    session_string: str
    account_name: str
    account_number: str
    bank_name: str

class BankAccountResponse(BaseModel):
    success: bool
    message: str

class TransactionRequest(BaseModel):
    username: str
    session_string: str
    account_id: int
    amount: float
    transaction_type: str
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    success: bool
    message: str

class AccountListResponse(BaseModel):
    success: bool
    accounts: List[dict]

@router.post("/create-account", response_model=BankAccountResponse)
async def create_account(request: BankAccountRequest, bank_db: Session = Depends(get_bank_db), account_db: Session = Depends(get_account_db)):
    """銀行口座作成API"""
    # セッション確認
    account = Account(request.username, account_db)
    if not account.verify_session(request.session_string):
        return BankAccountResponse(success=False, message="セッションが無効です")

    try:
        # 新しい銀行口座を作成
        bank_account = BankAccount(
            user_id=account.user_id,
            account_name=request.account_name,
            account_number=request.account_number,
            bank_name=request.bank_name,
            balance=0.00,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        bank_db.add(bank_account)
        bank_db.commit()

        return BankAccountResponse(success=True, message="口座が正常に作成されました")
    except Exception as e:
        bank_db.rollback()
        return BankAccountResponse(success=False, message=f"口座作成に失敗しました: {str(e)}")

@router.post("/add-transaction", response_model=TransactionResponse)
async def add_transaction(request: TransactionRequest, bank_db: Session = Depends(get_bank_db), account_db: Session = Depends(get_account_db)):
    """取引追加API"""
    # セッション確認
    account = Account(request.username, account_db)
    if not account.verify_session(request.session_string):
        return TransactionResponse(success=False, message="セッションが無効です")

    try:
        # 口座の存在確認
        bank_account = bank_db.query(BankAccount).filter(
            BankAccount.account_id == request.account_id,
            BankAccount.user_id == account.user_id
        ).first()

        if not bank_account:
            return TransactionResponse(success=False, message="口座が見つかりません")

        # 取引を追加
        transaction = Transaction(
            account_id=request.account_id,
            amount=request.amount,
            transaction_type=request.transaction_type,
            description=request.description,
            created_at=datetime.now()
        )
        bank_db.add(transaction)

        # 残高を更新
        if request.transaction_type == "deposit":
            bank_account.balance += request.amount
        elif request.transaction_type == "withdrawal":
            if bank_account.balance < request.amount:
                return TransactionResponse(success=False, message="残高が不足しています")
            bank_account.balance -= request.amount

        bank_account.updated_at = datetime.now()
        bank_db.commit()

        return TransactionResponse(success=True, message="取引が正常に追加されました")
    except Exception as e:
        bank_db.rollback()
        return TransactionResponse(success=False, message=f"取引追加に失敗しました: {str(e)}")

@router.post("/get-accounts", response_model=AccountListResponse)
async def get_accounts(request: dict, bank_db: Session = Depends(get_bank_db), account_db: Session = Depends(get_account_db)):
    """口座一覧取得API"""
    username = request.get("username")
    session_string = request.get("session_string")

    # セッション確認
    account = Account(username, account_db)
    if not account.verify_session(session_string):
        return AccountListResponse(success=False, accounts=[])

    try:
        # ユーザーの口座一覧を取得
        accounts = bank_db.query(BankAccount).filter(
            BankAccount.user_id == account.user_id
        ).all()

        account_list = []
        for acc in accounts:
            account_list.append({
                "account_id": acc.account_id,
                "account_name": acc.account_name,
                "account_number": acc.account_number,
                "bank_name": acc.bank_name,
                "balance": float(acc.balance)
            })

        return AccountListResponse(success=True, accounts=account_list)
    except Exception as e:
        return AccountListResponse(success=False, accounts=[])
