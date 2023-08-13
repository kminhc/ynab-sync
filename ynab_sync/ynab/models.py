from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class YNABTransaction(BaseModel):
    account_id: UUID
    date: date
    amount: int
    payee_name: str | None = Field(default="")
    memo: str = Field(default="")
    cleared: str
    approved: bool
    import_id: str


class YNABTransactions(BaseModel):
    transactions: list[YNABTransaction]


class YNABAccount(BaseModel):
    id: UUID
    name: str
    type: str
    balance: int
    closed: bool
    deleted: bool


class YNABBudget(BaseModel):
    id: UUID
    name: str
    last_modified_on: datetime
    first_month: date
    last_month: date
    date_format: dict
    currency_format: dict
    accounts: list[YNABAccount] = Field(default_factory=list)

    @property
    def currency(self):
        return self.currency_format["iso_code"]

    @property
    def currency_symbol(self):
        return self.currency_format["currency_symbol"]
