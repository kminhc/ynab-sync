import uuid
from collections import defaultdict

import appeal

# from gocardless.data import op_test_data
from gocardless.gocardless import GoCardLessAPI
from gocardless.models import GoCardlessBankAccountData
from ynab.models import YNABTransaction, YNABTransactions
from ynab.ynab import YnabAPI

app = appeal.Appeal()


# FIXME: not really working as I imagined :(
@app.command()
def upload(
    *,
    ynab_token: str = "",
    ynab_budget_id: str = "",
    ynab_account_id: str = "",
    gocardless_secret_id: str = "",
    gocardless_secret_key: str = "",
    gocardless_account_id: str = "",
    date_from: str = "",
    date_to: str = "",
):
    error = False
    for name, non_optional in {
        "ynab_token": ynab_token,
        "ynab_budget_id": ynab_budget_id,
        "ynab_account_id": ynab_account_id,
        "gocardless_secret_id": gocardless_secret_id,
        "gocardless_secret_key": gocardless_secret_key,
        "gocardless_account_id": gocardless_account_id,
    }.items():
        if not non_optional:
            print(f"`{name}` parameter should be specified.")
            error = True

    if error:
        return

    gocardless_api = GoCardLessAPI(
        secret_id=gocardless_secret_id, secret_key=gocardless_secret_key
    )
    ynab_api = YnabAPI(access_token=ynab_token)

    gocardless_transactions = gocardless_api.get_transactions(
        account_id=gocardless_account_id, date_from=date_from, date_to=date_to
    )

    # gocardless_transactions = GoCardlessBankAccountData(**op_test_data)

    transactions = []
    occurances = defaultdict(int)
    for gocardless_transaction in gocardless_transactions.transactions.booked:
        amount = int(gocardless_transaction.transaction_amount.amount * 1000)
        ynab_import_key = f"YNAB:{amount}:{gocardless_transaction.booking_date}"

        memo = (
            gocardless_transaction.remittance_information_unstructured
            or gocardless_transaction.proprietary_bank_transaction_code
            or ""
        )
        occurances[ynab_import_key] += 1
        transactions.append(
            YNABTransaction(
                account_id=ynab_account_id,
                date=gocardless_transaction.booking_date,
                amount=amount,
                payee_name=gocardless_transaction.creditor_name,
                memo=memo,
                cleared="cleared",
                approved=False,
                # import_id=gocardless_transaction.transaction_id,
                import_id=f"{ynab_import_key}:{occurances[ynab_import_key]}",
            )
        )

    ynab_transactions = YNABTransactions(transactions=transactions)

    response = ynab_api.post_transactions(
        budget_id=ynab_budget_id, json=ynab_transactions.model_dump_json()
    )

    print(response)
