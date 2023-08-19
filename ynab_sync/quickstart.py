from bullet import Bullet, YesNo
import os

from ynab_sync.constants import (
    ENV_GOCARDLESS_ACCOUNT_ID,
    ENV_GOCARDLESS_SECRET_ID,
    ENV_GOCARDLESS_SECRET_KEY,
    ENV_GOCARDLESS_COUNTRY,
    ENV_YNAB_ACCOUNT_ID,
    ENV_YNAB_BUDGET_ID,
    ENV_YNAB_TOKEN,
)
from ynab_sync.logic import (
    create_gocardless_requisition,
    get_gocardless_banks,
    get_gocardless_requisition,
    get_ynab_budget,
    get_ynab_budgets,
)

from .cli import app


def strip_secret(secret: str) -> str:
    return f"{secret[:5]}..{secret[-5:]}"


def default_value(value: str | None, strip: bool = False):
    if value:
        if strip:
            value = strip_secret(value)

        return f"({value})"
    return ""


def gocardless_prompt(debug: bool = False):
    env_secret_id = os.environ.get(ENV_GOCARDLESS_SECRET_ID, "")
    env_secret_key = os.environ.get(ENV_GOCARDLESS_SECRET_KEY, "")
    env_country = os.environ.get(ENV_GOCARDLESS_COUNTRY, "")

    print(
        "First, let's add GoCardless credentials and then I will help you ",
        "to connect your GoCardless account with your bank instititution.\n",
    )

    secret_id = input(f"Enter GoCardless Secret ID {default_value(env_secret_id, strip=True)}: ")
    secret_key = input(f"Enter GoCardless Secret Key {default_value(env_secret_key, strip=True)}: ")
    country = input(f"Enter your bank's country ISO code {default_value(env_country)}: ")

    print()

    secret_id = secret_id or env_secret_id
    secret_key = secret_key or env_secret_key
    country = country or env_country

    print(f"Getting list of bank from GoCardless for country {country}...\n")

    available_banks = get_gocardless_banks(
        secret_id=secret_id,
        secret_key=secret_key,
        country=country,
    )

    cli = Bullet(
        prompt="Choose your bank: ",
        choices=[bank.name for bank in available_banks],
        return_index=True,
    )  # type: ignore
    _, bank_index = cli.launch()
    bank = available_banks[bank_index]

    account_id = ""
    account_selected = False

    while not account_selected:
        print()
        print("Generating authorisation link...\n")

        created_requisition = create_gocardless_requisition(
            secret_id=secret_id,
            secret_key=secret_key,
            redirect="http://localhost",
            institution_id=bank.id,
        )

        print(
            f"Open this link in your browser and proceed with authorisation:\n",
        )
        print(created_requisition.link)
        print()
        input("Press Enter when you are ready.")
        print()

        print("Getting Account ID for your connection...\n")
        requisition = get_gocardless_requisition(
            secret_id=secret_id,
            secret_key=secret_key,
            requisition_id=created_requisition.id,
        )

        if not requisition.accounts:
            print("No Account ID was returned from GoCardless API. Regenerate link?\n")
            cli = YesNo("Regenerate the link? ")
            answer = cli.launch()
            if not answer:
                account_selected = True
        elif len(requisition.accounts) > 1:
            cli = Bullet(
                prompt="Looks like you have multiple accounts that you can use, choose one:",
                choices=requisition.accounts,
            )  # type: ignore
            account_id = cli.launch()
            account_selected = True
        else:
            account_id = requisition.accounts[0]
            account_selected = True

    return secret_id, secret_key, account_id


def ynab_prompt(debug: bool = False):
    print("\nNow let's configure YNAB credentials and I will help you get Budget and Account IDs\n")

    env_token = os.environ.get(ENV_YNAB_TOKEN)
    token = input(f"Enter YNAB access token {default_value(env_token, strip=True)}:") or env_token
    print()
    print("Getting YNAB budgets list...")

    budgets = get_ynab_budgets(token=token)

    cli = Bullet(
        prompt="Choose into which budget you want to upload transactions: ",
        choices=[budget.name for budget in budgets],
        return_index=True,
    )  # type: ignore
    _, budget_index = cli.launch()

    budget = budgets[budget_index]

    print()
    print(f"Getting account list for budget {budget.name}")

    budget = get_ynab_budget(token=token, budget_id=budget.id)

    cli = Bullet(
        prompt="Choose into which budget you want to upload transactions: ",
        choices=[account.name for account in budget.accounts],
        return_index=True,
    )  # type: ignore
    _, account_index = cli.launch()

    account = budget.accounts[account_index]

    return token, budget.id, account.id


@app.command()
def quickstart(*, debug: bool = False):
    print(
        "This tool will help you to generate .env file that ",
        "is nessesarry for `ynab-sync` upload to work.\n",
    )

    gocardless_secret_id, gocardless_secret_key, gocardless_account_id = gocardless_prompt(debug=debug)

    ynab_token, ynab_budget_id, ynab_account_id = ynab_prompt(debug=debug)

    print()
    print("These are environment variables that you can use in `upload` command")
    print()
    print(f"export {ENV_GOCARDLESS_SECRET_ID}={gocardless_secret_id}")
    print(f"export {ENV_GOCARDLESS_SECRET_KEY}={gocardless_secret_key}")
    print(f"export {ENV_GOCARDLESS_ACCOUNT_ID}={gocardless_account_id}")
    print(f"export {ENV_YNAB_TOKEN}={ynab_token}")
    print(f"export {ENV_YNAB_BUDGET_ID}={ynab_budget_id}")
    print(f"export {ENV_YNAB_ACCOUNT_ID}={ynab_account_id}")
