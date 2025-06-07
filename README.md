# AWS Cost Report Generator

This project uses Python and Ansible to generate a monthly AWS cost report by querying the AWS Cost Explorer API. It formats the results and emails the report to a specified list of recipients.

---

## Features

✅ Fetches monthly AWS costs broken down by service  
✅ Sorts and formats costs in a readable report  
✅ Sends the report via email using SMTP  
✅ Supports multiple AWS accounts  
✅ Uses environment variables for credentials (secure!)  
✅ Integrates with Ansible for automated runs

---

## Prerequisites

- **Python 3.6+**
- **Ansible 2.9+** (or any recent version that supports `ansible.builtin.command`)
- **AWS Cost Explorer enabled** in your AWS account(s)
- **IAM permissions** to call `ce:GetCostAndUsage` for the account(s)
- SMTP server information (configured in the script)
- Ansible Vault (optional but recommended) to securely store AWS credentials (called for in AWSCostReport.yml but can be removed)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aws-cost-report.git
   cd aws-cost-report
2. Install Python dependencies:
  ```bash
  pip install boto3
  ```

## Configuration

This project uses environment variables to provide AWS credentials securely:

| Variable                  | Description                  |
|---------------------------|------------------------------|
| AWS_ACCESS_KEY_ID_DEV     | Access key for account 1     |
| AWS_SECRET_ACCESS_KEY_DEV | Secret key for account 1     |
| AWS_ACCESS_KEY_ID_DEV2    | Access key for account 2     |
| AWS_SECRET_ACCESS_KEY_DEV2| Secret key for account 2     |
| AWS_ACCESS_KEY_ID_DEV3    | Access key for account 3     |
| AWS_SECRET_ACCESS_KEY_DEV3| Secret key for account 3     |

> **Tip:** You can export them in your shell or use Ansible Vault (recommended for production).

## Run it:
  bash
  `ansible-playbook -i localhost, AWSCostReport.yml`
