from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any

from pydantic import BaseModel, Field, model_validator


class GoCardlessTransactionAmount(BaseModel):
    amount: Decimal
    currency: str


class GoCardlessTransaction(BaseModel):
    transaction_id: str = Field(alias="transactionId")
    booking_date: Optional[date] = Field(alias="bookingDate", default=None)
    value_date: Optional[date] = Field(alias="valueDate", default=None)
    transaction_amount: GoCardlessTransactionAmount = Field(alias="transactionAmount")
    debtor_name: Optional[str] = Field(alias="debtorName", default=None)
    creditor_name: Optional[str] = Field(alias="creditorName", default=None)
    debtor_account: Optional[dict] = Field(alias="debtorAccount", default=None)
    remittance_information_unstructured: str = Field(alias="remittanceInformationUnstructured", default="")
    proprietary_bank_transaction_code: Optional[str] = Field(alias="proprietaryBankTransactionCode", default=None)


    @model_validator(mode='before')
    @classmethod
    def set_default_dates(cls, data: Any ):
        booking_date = data.get('bookingDate')
        value_date = data.get('valueDate')

        if not booking_date and not value_date:
            raise ValueError('At least one of bookingDate or valueDate must be provided')

        if not booking_date:
            data['bookingDate'] = value_date
        if not value_date:
            data['valueDate'] = booking_date
        return data

    bank_transaction_code: Optional[str] = Field(alias="bankTransactionCode", default=None)

class GoCardlessPendingTransaction(GoCardlessTransaction):
    transaction_id: Optional[str] = Field(alias="transactionId", default=None)


class GoCardlessTransactions(BaseModel):
    booked: list[GoCardlessTransaction]
    pending: list[GoCardlessPendingTransaction]


class GoCardlessBankAccountData(BaseModel):
    transactions: GoCardlessTransactions


class GoCardlessInstitution(BaseModel):
    id: str
    name: str


class GoCardlessRequisition(BaseModel):
    id: str
    created: datetime
    redirect: str
    status: str
    institution_id: str
    link: str
    accounts: list[str] = Field(default_factory=list)
