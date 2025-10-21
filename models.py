from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .config import BankBase

class BankAccount(BankBase):
    __tablename__ = "bank_accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    bank_name = Column(String(255), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Transaction(BankBase):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("bank_accounts.account_id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'deposit', 'withdrawal', 'transfer'
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False)
