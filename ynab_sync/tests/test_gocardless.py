import os

import pytest
from ynab_sync.gocardless.gocardless import GoCardLessAPI

SECRET_ID = os.getenv("GOCARDLESS_SECRET_ID", "")
SECRET_KEY = os.getenv("GOCARDLESS_SECRET_KEY", "")
ACCOUNT_ID = os.getenv("GOCARDLESS_ACCOUNT_ID", "")


def test_auth():
    api = GoCardLessAPI(secret_id=SECRET_ID, secret_key=SECRET_KEY)
    transactions = api.get_transactions(account_id=ACCOUNT_ID)
    print(transactions)
    assert False
