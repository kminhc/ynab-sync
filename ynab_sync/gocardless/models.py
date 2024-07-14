from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.v1 import root_validator


class GoCardlessTransactionAmount(BaseModel):
    amount: Decimal
    currency: str


class GoCardlessTransaction(BaseModel):
    transaction_id: str = Field(alias="transactionId")
    booking_date: Optional[date] = Field(alias="bookingDate", default=None)
    value_date: Optional[date] = Field(alias="valueDate", default=None)
    transaction_amount: GoCardlessTransactionAmount = Field(alias="transactionAmount")
    debtor_name: str | None = Field(alias="debtorName", default=None)
    creditor_name: str | None = Field(alias="creditorName", default=None)
    debtor_account: dict | None = Field(alias="debtorAccount", default=None)
    remittance_information_unstructured: str = Field(alias="remittanceInformationUnstructured", default="")
    proprietary_bank_transaction_code: str | None = Field(alias="proprietaryBankTransactionCode", default=None)
    bank_transaction_code: str | None = Field(alias="bankTransactionCode", default=None)

    @root_validator(pre=True)
    def set_default_dates(cls, values):
        booking_date = values.get('bookingDate')
        value_date = values.get('valueDate')

        if not booking_date and not value_date:
            raise ValueError('At least one of bookingDate or valueDate must be provided')

        if not booking_date:
            values['bookingDate'] = value_date
        if not value_date:
            values['valueDate'] = booking_date

        return values

class GoCardlessPendingTransaction(GoCardlessTransaction):
    transaction_id: str | None = Field(alias="transactionId", default=None)


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
