import datetime
import uuid

import appeal

app = appeal.Appeal()


@app.command()
def upload(
    ynab_token: uuid.UUID,
    ynab_budget_id: uuid.UUID,
    ynab_account_id: uuid.UUID,
    gocardless_secret_id: str,
    gocardless_secret_key: str,
    gocardless_account_id: uuid.UUID,
    date_from: str,
    date_to: str,
):
    print(f"Hello, {name}!")
