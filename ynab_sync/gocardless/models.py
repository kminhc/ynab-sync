from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionAmount(BaseModel):
    amount: Decimal
    currency: str


class Transaction(BaseModel):
    transaction_id: str = Field(alias="transactionId")
    booking_date: date = Field(alias="bookingDate")
    value_date: date = Field(alias="valueDate")
    transaction_amount: TransactionAmount = Field(alias="transactionAmount")
    debtor_name: str | None = Field(alias="debtorName", default=None)
    debtor_account: dict | None = Field(alias="debtorAccount", default=None)
    remittance_information_unstructured: str = Field(
        alias="remittanceInformationUnstructured"
    )
    bank_transaction_code: str = Field(alias="bankTransactionCode")


class Transactions(BaseModel):
    booked: list[Transaction]
    pending: list[dict]


class BankAccountData(BaseModel):
    transactions: Transactions
