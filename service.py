from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from .models import BankAccount, Transaction

class BankService:
    def __init__(self, db: Session):
        self.db = db

    def create_account(self, user_id: int, account_name: str, account_number: str, bank_name: str) -> Optional[BankAccount]:
        """銀行口座を作成"""
        try:
            bank_account = BankAccount(
                user_id=user_id,
                account_name=account_name,
                account_number=account_number,
                bank_name=bank_name,
                balance=Decimal('0.00'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(bank_account)
            self.db.commit()
            return bank_account
        except Exception:
            self.db.rollback()
            return None

    def get_user_accounts(self, user_id: int) -> List[BankAccount]:
        """ユーザーの口座一覧を取得"""
        return self.db.query(BankAccount).filter(BankAccount.user_id == user_id).all()

    def get_account_by_id(self, account_id: int, user_id: int) -> Optional[BankAccount]:
        """特定の口座を取得"""
        return self.db.query(BankAccount).filter(
            BankAccount.account_id == account_id,
            BankAccount.user_id == user_id
        ).first()

    def add_transaction(self, account_id: int, amount: Decimal, transaction_type: str, description: str = None) -> Optional[Transaction]:
        """取引を追加"""
        try:
            # 口座の存在確認
            account = self.db.query(BankAccount).filter(BankAccount.account_id == account_id).first()
            if not account:
                return None

            # 残高チェック（出金の場合）
            if transaction_type == "withdrawal" and account.balance < amount:
                return None

            # 取引を追加
            transaction = Transaction(
                account_id=account_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                created_at=datetime.now()
            )
            self.db.add(transaction)

            # 残高を更新
            if transaction_type == "deposit":
                account.balance += amount
            elif transaction_type == "withdrawal":
                account.balance -= amount

            account.updated_at = datetime.now()
            self.db.commit()
            return transaction
        except Exception:
            self.db.rollback()
            return None

    def get_account_transactions(self, account_id: int, user_id: int) -> List[Transaction]:
        """口座の取引履歴を取得"""
        # 口座の所有権を確認
        account = self.get_account_by_id(account_id, user_id)
        if not account:
            return []

        return self.db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).order_by(Transaction.created_at.desc()).all()
