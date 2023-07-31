import json
import os
from pprint import pprint

import pytest
from ynab_sync.gocardless.gocardless import GoCardLessAPI
from ynab_sync.gocardless.models import BankAccountData
from ynab_sync.tests.data.gocardless import \
    TRANSACTIONS as GOCARDLESS_TRANSACTIONS

SECRET_ID = os.getenv("GOCARDLESS_SECRET_ID", "")
SECRET_KEY = os.getenv("GOCARDLESS_SECRET_KEY", "")
ACCOUNT_ID = os.getenv("GOCARDLESS_ACCOUNT_ID", "")


def test_auth():
    api = GoCardLessAPI(secret_id=SECRET_ID, secret_key=SECRET_KEY)
    transactions = api.get_transactions(account_id=ACCOUNT_ID)
    data = BankAccountData(**transactions)
    pprint(data)
    assert False


def test_bank_account_data_model():
    data = BankAccountData(**json.loads(GOCARDLESS_TRANSACTIONS))
    print(data)
    assert False
