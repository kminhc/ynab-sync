from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class GoCardlessTransactionAmount(BaseModel):
    amount: Decimal
    currency: str


class GoCardlessTransaction(BaseModel):
    transaction_id: str = Field(alias="transactionId")
    booking_date: date = Field(alias="bookingDate")
    value_date: date = Field(alias="valueDate")
    transaction_amount: GoCardlessTransactionAmount = Field(alias="transactionAmount")
    debtor_name: str | None = Field(alias="debtorName", default=None)
    creditor_name: str | None = Field(alias="creditorName", default=None)
    debtor_account: dict | None = Field(alias="debtorAccount", default=None)
    remittance_information_unstructured: str = Field(
        alias="remittanceInformationUnstructured", default=""
    )
    proprietary_bank_transaction_code: str | None = Field(
        alias="proprietaryBankTransactionCode", default=None
    )
    bank_transaction_code: str | None = Field(alias="bankTransactionCode", default=None)


class GoCardlessTransactions(BaseModel):
    booked: list[GoCardlessTransaction]
    pending: list[dict]


class GoCardlessBankAccountData(BaseModel):
    transactions: GoCardlessTransactions
