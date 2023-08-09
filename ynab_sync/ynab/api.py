import json
import uuid

import requests

BASE_URL = "https://api.ynab.com/v1"


class YnabAPI:
    def __init__(self, access_token: str):
        self._access_token: str = access_token
        self._request_session: requests.Session | None = None

    @property
    def _requests_session(self) -> requests.Session:
        if self._request_session is None:
            self._request_session = requests.Session()
            self._request_session.headers.update(
                {"Authorization": f"Bearer {self._access_token}"}
            )

        return self._request_session

    @staticmethod
    def _get_transaction_url(
        budget_id: uuid.UUID,
    ) -> str:
        url = f"{BASE_URL}/budgets/{budget_id}/transactions/"

        return url

    def post_transactions(
        self,
        budget_id: uuid.UUID,
        json_data: str,
    ) -> dict:
        response = self._requests_session.post(
            self._get_transaction_url(
                budget_id=budget_id,
            ),
            json=json.loads(json_data),
        )
        response.raise_for_status()

        return response.json()
