import os
import sys
import boto3
import datetime
import logging
import smtplib
from email.message import EmailMessage

# SMTP CONFIGURATION
SMTP_SERVER = "mail.corp.example.net" # input your mailing server here
SMTP_PORT = 25
SMTP_USERNAME = "DONOTREPLY@example.com" # input mailing address here
SMTP_SENDER = SMTP_USERNAME
SMTP_RECIPIENTS = ['user1@example.com', 'user2@example.com'] # input desired recipient email addresses here

# Read accounts from environment variables (vaulted via Ansible)
ACCOUNTS = [
    {
        "name": "", # ex. it-dev
        "account_id": "", # ex. 12345678
        "access_key": os.getenv("AWS_ACCESS_KEY_ID_DEV"), # adjust based on varible name you chose in the vault file
        "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_DEV"), # adjust based on varible name you chose in the vault file
        "region": "" # ex. us-east-2
    },
    {
        "name": "",
        "account_id": "",
        "access_key": os.getenv("AWS_ACCESS_KEY_ID_DEV2"),
        "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_DEV2"),
        "region": ""
    },
    {
        "name": "",
        "account_id": "",
        "access_key": os.getenv("AWS_ACCESS_KEY_ID_DEV3"),
        "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_DEV3"),
        "region": ""
    }
    # add as many as needed
]

# HELPERS

def get_last_month_range():
    today = datetime.date.today()
    first_of_this_month = today.replace(day=1)
    last_of_prev_month = first_of_this_month - datetime.timedelta(days=1)
    start = last_of_prev_month.replace(day=1).isoformat()
    end = last_of_prev_month.isoformat()
    label = last_of_prev_month.strftime('%B %Y')
    return start, end, label

def fetch_costs(session, start, end):
    ce = session.client('ce')
    resp = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    return resp['ResultsByTime'][0]

def format_report(result, label, start, end, account_name):
    lines = [
        f"AWS Cost Report for {label} ({start} to {end})",
        f"Account: {account_name}",
        "=" * 50
    ]

    groups = result.get('Groups', [])

    svc_costs = []
    for g in groups:
        svc = g['Keys'][0]
        amt = float(g['Metrics']['UnblendedCost']['Amount'])
        if round(amt, 2) == 0.00:
            continue
        svc_costs.append((svc, amt))

    svc_costs.sort(key=lambda x: x[1], reverse=True)
    total = sum(amt for _, amt in svc_costs)

    for svc, amt in svc_costs:
        lines.append(f"{svc:30s} ${amt:>10,.2f}")
    lines.append("-" * 50)
    lines.append(f"{'TOTAL':30s} ${total:>10,.2f}")

    return "\n".join(lines)

def send_email_smtp(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_SENDER
    msg['To'] = ', '.join(SMTP_RECIPIENTS)
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
        logging.info("Email sent via SMTP.")
    except Exception as e:
        logging.error("Failed to send email via SMTP: %s", e)
        sys.exit(1)

# MAIN

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    start, end, label = get_last_month_range()
    logging.info("Generating reports for %s → %s", start, end)

    for acct in ACCOUNTS:
        logging.info("Processing account: %s", acct['name'])

        if not acct['access_key'] or not acct['secret_key']:
            logging.error("Missing credentials for %s", acct['name'])
            continue

        session = boto3.Session(
            aws_access_key_id=acct['access_key'],
            aws_secret_access_key=acct['secret_key'],
            region_name=acct['region']
        )

        try:
            result = fetch_costs(session, start, end)
            report = format_report(result, label, start, end, acct['name'])
            subject = f"AWS Cost Report for {acct['name']} – {label}"
            send_email_smtp(subject, report)
        except Exception as e:
            logging.error("Error processing account %s: %s", acct['name'], e)

if __name__ == '__main__':
    main()
