import uuid
from datetime import date

import requests

from .models import GoCardlessBankAccountData, GoCardlessInstitution

BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"


class GoCardLessAPI:
    def __init__(self, secret_id: str, secret_key: str):
        self._secret_id = secret_id
        self._secret_key = secret_key
        self._access_token: str | None = None
        self._request_session: requests.Session | None = None

    def _get_token(
        self,
    ) -> str:
        if self._access_token is None:
            url = f"{BASE_URL}/token/new/"
            body = {"secret_key": self._secret_key, "secret_id": self._secret_id}
            response = requests.post(url, json=body)
            response_json = response.json()
            self._access_token = response_json["access"]

        return self._access_token

    @property
    def _requests_session(self) -> requests.Session:
        if self._request_session is None:
            self._request_session = requests.Session()
            self._request_session.headers.update(
                {"Authorization": f"Bearer {self._get_token()}"}
            )

        return self._request_session

    @staticmethod
    def _get_transaction_url(
        account_id: uuid.UUID,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> str:
        url = f"{BASE_URL}/accounts/{account_id}/transactions/?"
        if date_from:
            url += f"date_from={date_from}"
        if date_to:
            url += f"date_to={date_to}"

        return url

    def get_transactions(
        self,
        account_id: uuid.UUID,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> GoCardlessBankAccountData:
        response = self._requests_session.get(
            self._get_transaction_url(
                account_id=account_id,
                date_from=date_from,
                date_to=date_to,
            )
        )
        response.raise_for_status()
        json_data = response.json()
        return GoCardlessBankAccountData(**json_data)

    def get_banks(self, country: str) -> list[GoCardlessInstitution]:
        response = self._requests_session.get(
            f"{BASE_URL}/institutions/?country={country}"
        )
        response.raise_for_status()
        json_data = response.json()
        return [GoCardlessInstitution(**institution) for institution in json_data]
