# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /ynab-sync

# Copy the current directory contents into the container at /app
COPY . /ynab-sync

# Run the command to install any necessary dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run hello.py when the container launches
CMD ["sh", "-c", "python ynab_sync upload --ynab-token=$YNAB_TOKEN --ynab-budget-id=$YNAB_BUDGET_ID --ynab-account-id=$YNAB_ACCOUNT_ID --gocardless-secret-id=$GOCARDLESS_SECRET_ID --gocardless-secret-key=$GOCARDLESS_SECRET_KEY --gocardless-account-id=$GOCARDLESS_ACCOUNT_ID --date-from=`date -d '-7 day' '+%Y-%m-%d'`"]
