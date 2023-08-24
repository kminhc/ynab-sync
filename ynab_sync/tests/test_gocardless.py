import json
import os
from pprint import pprint

import pytest

from ..gocardless.api import GoCardLessAPI
from ..gocardless.models import GoCardlessBankAccountData
from .data.gocardless import TEST_GOCARDLESS_TRANSACTIONS as GOCARDLESS_TRANSACTIONS

SECRET_ID = os.getenv("GOCARDLESS_SECRET_ID", "")
SECRET_KEY = os.getenv("GOCARDLESS_SECRET_KEY", "")
ACCOUNT_ID = os.getenv("GOCARDLESS_ACCOUNT_ID", "")


@pytest.mark.skip("Manual test")
def test_auth():
    api = GoCardLessAPI(secret_id=SECRET_ID, secret_key=SECRET_KEY)
    transactions = api.get_transactions(account_id=ACCOUNT_ID)
    pprint(data)
    assert False


@pytest.mark.skip("Manual test")
def test_bank_account_data_model():
    data = GoCardlessBankAccountData(**json.loads(GOCARDLESS_TRANSACTIONS))
    print(data)
    assert False
