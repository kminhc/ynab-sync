import json
from http import HTTPStatus
from uuid import uuid4

import pytest
import responses

from ..cli import upload
from ..gocardless.api import BASE_URL as GOCARDLESS_BASE_URL
from ..tests.data.gocardless import TEST_GOCARDLESS_TRANSACTIONS
from ..tests.data.ynab import (TEST_YNAB_REQUEST_TRANSACTIONS,
                               TEST_YNAB_RESPONSE_TRANSACTIONS)
from ..ynab.api import BASE_URL as YNAB_BASE_URL

TEST_YNAB_TOKEN = "TEST_YNAB_TOKEN"
TEST_YNAB_BUDGET_ID = "49c714fa-fa82-4e11-b145-1e1d87a61c1f"
TEST_YNAB_ACCOUNT_ID = "93ec6d1f-7d75-48de-85b4-d9caec4807c8"
TEST_GOCARDLESS_SECRET_ID = "TEST_GOCARDLESS_SECRET_ID"
TEST_GOCARDLESS_SECRET_KEY = "TEST_GOCARDLESS_SECRET_KEY"
TEST_GOCARDLESS_ACCOUNT_ID = "dcefb08b-bb77-4a16-ab9f-e8f509de8ec6"
TEST_GOCARDLESS_ACCESS_TOKEN = "TEST_GOCARDLESS_ACCESS_TOKEN"
TEST_GOCARDLESS_REFRESH_TOKEN = "TEST_GOCARDLESS_REFRESH_TOKEN"


@pytest.fixture(name="gocardless_new_token_response", scope="module", autouse=True)
def fixture_gocardless_new_token_response() -> None:
    responses.add(
        responses.POST,
        f"{GOCARDLESS_BASE_URL}/token/new/",
        json={
            "access": TEST_GOCARDLESS_ACCESS_TOKEN,
            "refresh": TEST_GOCARDLESS_REFRESH_TOKEN,
        },
        status=HTTPStatus.OK,
        match=[
            responses.matchers.json_params_matcher(
                {
                    "secret_id": TEST_GOCARDLESS_SECRET_ID,
                    "secret_key": TEST_GOCARDLESS_SECRET_KEY,
                }
            )
        ],
    )


# TODO: Support date_from and date_to parameters
@pytest.fixture(name="gocardless_get_transactions", scope="module", autouse=True)
def fixture_gocardless_get_transactions() -> None:
    responses.add(
        responses.GET,
        f"{GOCARDLESS_BASE_URL}/accounts/{TEST_GOCARDLESS_ACCOUNT_ID}/transactions/?",
        json=json.loads(TEST_GOCARDLESS_TRANSACTIONS),
        status=HTTPStatus.OK,
        match=[
            responses.matchers.header_matcher(
                {"Authorization": f"Bearer {TEST_GOCARDLESS_ACCESS_TOKEN}"}
            ),
            # TODO: add date_from/date_to matcher
        ],
    )


@pytest.fixture(name="ynab_get_transactions", scope="module", autouse=True)
def fixture_ynab_post_transactions() -> None:
    responses.add(
        responses.POST,
        f"{YNAB_BASE_URL}/budgets/{TEST_YNAB_BUDGET_ID}/transactions/",
        json=json.loads(TEST_YNAB_RESPONSE_TRANSACTIONS),
        status=HTTPStatus.OK,
        match=[
            responses.matchers.header_matcher(
                {"Authorization": f"Bearer {TEST_YNAB_TOKEN}"}
            ),
            responses.matchers.json_params_matcher(
                json.loads(TEST_YNAB_REQUEST_TRANSACTIONS)
            ),
        ],
    )


@pytest.mark.parametrize("date_from, date_to", ([None, None],))
@responses.activate
def test_upload_e2e(date_from: str, date_to: str):
    upload(
        ynab_token=TEST_YNAB_TOKEN,
        ynab_budget_id=TEST_YNAB_BUDGET_ID,
        ynab_account_id=TEST_YNAB_ACCOUNT_ID,
        gocardless_secret_id=TEST_GOCARDLESS_SECRET_ID,
        gocardless_account_id=TEST_GOCARDLESS_ACCOUNT_ID,
        gocardless_secret_key=TEST_GOCARDLESS_SECRET_KEY,
        date_from=date_from,
        date_to=date_to,
    )
