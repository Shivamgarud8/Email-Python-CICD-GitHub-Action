# Multi-Cloud Data Migration Pipeline (AWS to Azure)

> An end-to-end automated data pipeline that captures user data from a web application, persists it in a relational database, and migrates it across cloud platforms — from AWS DynamoDB to Azure Cosmos DB — using Python automation scripts.

---

## Table of Contents

- [Project Summary](#project-summary)
- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
  - [1. AWS EC2 Server Setup](#1-aws-ec2-server-setup)
  - [2. Web Application Setup](#2-web-application-setup)
  - [3. MariaDB Configuration](#3-mariadb-configuration)
  - [4. AWS IAM and CLI Configuration](#4-aws-iam-and-cli-configuration)
  - [5. DynamoDB Table Setup](#5-dynamodb-table-setup)
  - [6. MariaDB to DynamoDB Migration](#6-mariadb-to-dynamodb-migration)
  - [7. Azure Cosmos DB Setup](#7-azure-cosmos-db-setup)
  - [8. DynamoDB to Cosmos DB Migration](#8-dynamodb-to-cosmos-db-migration)
  - [9. Security and Credential Handling](#9-security-and-credential-handling)
  - [10. GitHub Integration](#10-github-integration)
- [Key Features](#key-features)
- [Learning Outcomes](#learning-outcomes)
- [Future Enhancements](#future-enhancements)

---

## Project Summary

This project demonstrates a real-world, production-style multi-cloud data migration pipeline. A PHP-backed HTML form collects user data and stores it in a MariaDB instance running on AWS EC2. Two Python migration scripts then move the data sequentially — first from MariaDB into AWS DynamoDB, then from DynamoDB into Azure Cosmos DB — handling SQL-to-NoSQL transformation, pagination, and secure credential management throughout.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 |
| Backend | PHP |
| Local Database | MariaDB (on EC2) |
| AWS NoSQL | Amazon DynamoDB |
| Azure NoSQL | Azure Cosmos DB (Core SQL API) |
| Cloud Compute | Amazon EC2 |
| Identity & Access | AWS IAM |
| Migration Scripts | Python 3, Boto3, azure-cosmos, pymysql |
| Version Control | Git, GitHub |

---

## Architecture Overview

```
User Browser
     |
HTML Form (index.html)
     |
PHP Backend — submit.php
     |
MariaDB (AWS EC2) — DB: user_app / Table: users
     |
Python Script: migrate_to_dynamo.py  (pymysql + boto3)
     |
AWS DynamoDB — Region: eu-north-1 / Table: users
     |
Python Script: migrate_to_cosmos.py  (boto3 + azure-cosmos)
     |
Azure Cosmos DB — Core SQL API / DB: user_db / Container: users
```

Data flow: User input → HTML form → PHP → MariaDB → DynamoDB (AWS) → Cosmos DB (Azure)

---

## Prerequisites

Before starting, ensure you have the following ready:

- An active AWS account with permissions to create EC2, DynamoDB, and IAM resources
- An active Azure account with permissions to create Cosmos DB resources
- A local machine with Git installed
- Basic familiarity with Linux terminal commands

---

## Step-by-Step Setup

---

### 1. AWS EC2 Server Setup

**Launch an EC2 instance**

1. Log in to the AWS Management Console at console.aws.amazon.com.
2. Navigate to EC2 > Instances > Launch Instance.
3. Select Amazon Linux 2 or Ubuntu 22.04 LTS as the AMI.
4. Choose instance type `t2.micro`, which is free tier eligible.
5. Under security group settings, allow inbound traffic on port 22 for SSH and port 80 for HTTP.
6. Create or select an existing key pair, download the `.pem` file, and launch the instance.

**Connect to the instance**

Use SSH from your local terminal with the downloaded `.pem` key file and the EC2 public IP address. Ensure the key file has the correct restricted permissions before attempting to connect, otherwise SSH will refuse to use it.

**Install required packages**

Once connected via SSH, update all system packages first. Then install the following on the server: Apache web server, PHP and its MySQL extension, MariaDB server, Python 3, and pip. The exact package names differ slightly between Amazon Linux and Ubuntu — refer to the repository for the distro-specific install commands. After installation, start and enable both the Apache and MariaDB services so they survive reboots automatically.

---

### 2. Web Application Setup

**HTML form — index.html**

Place an HTML file at `/var/www/html/index.html`. The form collects three fields from the user: Name, Phone, and Age. The form method is POST and the action points to `submit.php` in the same directory.

**PHP handler — submit.php**

Place a PHP script at `/var/www/html/submit.php`. This script is responsible for:

1. Opening a connection to the local MariaDB instance using the root credentials and the `user_app` database.
2. Reading the three POST values submitted by the form: name, phone, and age.
3. Inserting those values into the `users` table using a prepared statement to prevent SQL injection.
4. Returning a plain-text success message to the browser on completion.

All database credentials in this file should be moved to environment variables before any version control commit.

---

### 3. MariaDB Configuration

**Secure the installation**

After installing MariaDB, run the built-in secure installation utility. It will walk you through setting a root password, removing anonymous users, disabling remote root login, and dropping the default test database. Accept all recommended options. This step is mandatory before exposing the database to any application.

**Set the root password**

During the secure installation wizard you will be prompted to set a root password. Choose a strong password and record it securely — you will need it when configuring the PHP backend and the Python migration script.

**Create the database**

Log in to the MariaDB shell as root using your new password. Create a database named `user_app` and switch to it.

**Create the users table**

Inside `user_app`, create a table named `users` with the following columns:

- `user_id` — integer, auto-incrementing, primary key
- `name` — varchar, up to 100 characters
- `phone` — varchar, up to 20 characters
- `age` — integer

Run a show tables command to verify the table exists and a describe command to confirm the column structure matches the above before proceeding.

---

### 4. AWS IAM and CLI Configuration

**Create an IAM user for programmatic access**

1. Log in to the AWS Console and navigate to IAM > Users > Add User.
2. Choose a username such as `migration-bot`.
3. Select the Programmatic access option so an access key pair is generated.
4. On the permissions screen, attach the `AmazonDynamoDBFullAccess` managed policy directly to the user.
5. Complete the wizard and immediately save the Access Key ID and Secret Access Key. They are only shown once.

**Create an IAM role for the EC2 instance (recommended)**

Attaching an IAM role to the EC2 instance is more secure than storing access keys on disk, because credentials are rotated automatically by AWS and never touch the filesystem.

1. Go to IAM > Roles > Create Role.
2. Select AWS Service and choose EC2 as the trusted entity.
3. Attach the `AmazonDynamoDBFullAccess` managed policy.
4. Name the role, for example `ec2-dynamodb-migration-role`, and complete the creation.
5. In the EC2 console, select your instance and go to Actions > Security > Modify IAM Role. Attach the role you just created.

Once the role is attached, any AWS SDK or CLI call made from that EC2 instance will automatically authenticate using the role — no access keys required.

**Configure the AWS CLI on EC2**

Install the AWS CLI using pip if it is not already present. Run the `aws configure` command and provide your Access Key ID, Secret Access Key, default region as `eu-north-1`, and output format as `json`. After configuring, verify the setup with `aws sts get-caller-identity` — it should return your account ID and IAM user or role details.

---

### 5. DynamoDB Table Setup

**Create the table via AWS CLI**

Use the AWS CLI to create a DynamoDB table named `users` in the `eu-north-1` region. The table requires a single attribute named `user_id` of type Number, configured as the HASH partition key. Set the billing mode to PAY_PER_REQUEST so you are charged only for actual reads and writes rather than provisioned capacity.

**Verify the table**

Run the describe-table command targeting the `users` table in `eu-north-1`. Confirm that the table status is ACTIVE before running any migration script against it.

---

### 6. MariaDB to DynamoDB Migration

**Install Python dependencies**

Install the `pymysql` and `boto3` packages using pip3 on the EC2 instance. The `pymysql` library handles the connection to MariaDB and the `boto3` library provides the AWS SDK interface for writing to DynamoDB.

**How the migration script works — migrate_to_dynamo.py**

The script performs these steps in order:

1. Opens a connection to the local MariaDB `user_app` database using pymysql and the root credentials.
2. Executes a SELECT query to fetch all rows from the `users` table, retrieving user_id, name, phone, and age for each record.
3. Opens a DynamoDB resource connection via boto3 targeting the `eu-north-1` region.
4. Iterates over every row fetched from MariaDB and calls put_item on the DynamoDB `users` table, mapping each SQL column directly to its NoSQL equivalent key.
5. Increments a counter for each successful write and prints the total on completion.

After running the script, verify the records in the AWS DynamoDB console under the `users` table in `eu-north-1`. You should see one item per user that was registered through the web form.

---

### 7. Azure Cosmos DB Setup

**Create a Cosmos DB account**

1. Log in to the Azure Portal at portal.azure.com.
2. Click Create a resource and search for Azure Cosmos DB.
3. Select Core (SQL) API as the API type. This API is compatible with standard SQL-style queries and is the most widely supported option.
4. Fill in the configuration details:
   - Subscription: select your active Azure subscription
   - Resource Group: create a new group named `migration-rg`
   - Account Name: choose something unique, for example `user-migration-cosmos`
   - Location: pick the Azure region closest to your EC2 instance to reduce latency
   - Capacity Mode: choose Serverless to avoid paying for unused provisioned throughput
5. Click Review + Create and then Create. Deployment typically takes 3 to 5 minutes.

**Create the database**

Once deployment is complete, go to your Cosmos DB account and open Data Explorer from the left navigation panel. Click New Database, set the Database ID to `user_db`, and click OK.

**Create the container**

Inside `user_db`, click New Container and fill in the following fields:

- Database ID: select `user_db` (existing)
- Container ID: `users`
- Partition Key: `/user_id`

Click OK. The partition key determines how Cosmos DB distributes data internally — using `user_id` ensures each record lands in its own logical partition.

**Retrieve connection credentials**

In your Cosmos DB account, navigate to Settings > Keys in the left panel. You will see two values you need:

- URI — this is the full HTTPS endpoint for your account
- PRIMARY KEY — the secret key used to authenticate requests

Copy both values. On your EC2 instance, set them as environment variables named `AZURE_COSMOS_ENDPOINT` and `AZURE_COSMOS_KEY` respectively. To make them persist across sessions, add the export statements to your `~/.bashrc` or `~/.bash_profile` file and source it.

Never paste these credentials directly into a Python script or commit them to any repository.

---

### 8. DynamoDB to Cosmos DB Migration

**Install Python dependencies**

Install `boto3` and `azure-cosmos` using pip3. The `boto3` library reads from DynamoDB and the `azure-cosmos` library writes to Cosmos DB.

**How the migration script works — migrate_to_cosmos.py**

The script performs these steps in sequence:

1. Reads `AZURE_COSMOS_ENDPOINT` and `AZURE_COSMOS_KEY` from environment variables. The script exits immediately with a clear error if either variable is missing, preventing silent failures.
2. Initializes a CosmosClient with the endpoint and key, then gets client references to the `user_db` database and the `users` container.
3. Initializes a boto3 DynamoDB resource pointing at `eu-north-1` and references the `users` table.
4. Runs a paginated scan of the DynamoDB table. DynamoDB returns results in pages of up to 1 MB, so the script checks for a `LastEvaluatedKey` in each response and continues scanning until that key is absent, meaning all pages have been consumed.
5. For each item, runs a recursive Decimal conversion function that walks the dictionary and replaces every Python Decimal value with a standard int or float. DynamoDB uses Decimal internally for all numbers; Cosmos DB does not accept this type and will raise an error without this conversion step.
6. Adds an `id` field to each item by converting the `user_id` value to a string. Cosmos DB requires every document to contain a field literally named `id` as a string — this is non-negotiable.
7. Calls upsert_item on the Cosmos container for each converted record. Upsert means that if a document with the same `id` already exists in Cosmos DB it will be overwritten rather than creating a duplicate or raising an error, making the script safe to run multiple times.
8. Prints the total number of records successfully upserted when the loop completes.

**Verify the migration in Azure Portal**

After the script finishes, open the Azure Portal and navigate to your Cosmos DB account. Go to Data Explorer > user_db > users > Items. All migrated records should appear here with their user_id, name, phone, and age fields intact.

---

### 9. Security and Credential Handling

Following secure practices throughout this project is non-negotiable. These are the rules applied at every stage:

- No credentials, API keys, or passwords are hardcoded anywhere in the source files.
- All sensitive values are injected at runtime through environment variables.
- A `.gitignore` file is created before the first commit to exclude `.env` files, `.pem` key files, Python `__pycache__` folders, and compiled `.pyc` files.
- If a credential is ever accidentally committed to Git history, it must be rotated immediately. For AWS, go to IAM > Security credentials to generate new access keys and deactivate the old ones. For Azure, go to Cosmos DB account > Settings > Keys and regenerate the primary key. Never simply delete the credential from the file and recommit — the secret remains in Git history until history is rewritten.
- To remove secrets from Git history before pushing to a public repository, use the BFG Repo Cleaner tool or the `git filter-branch` command. Both tools rewrite commit history to eliminate the offending data.
- GitHub's secret scanning feature will automatically reject pushes that contain detected AWS keys or Azure keys. If a push is blocked, history rewriting is required before it will be accepted.

---

### 10. GitHub Integration

**Initialize the repository**

Run `git init` in the root of your project directory to initialize a new local repository.

**Create a .gitignore file**

Before staging any files, create a `.gitignore` that excludes the following: `.env` files, `.pem` key files, `__pycache__` directories, and `.pyc` compiled Python files. This prevents secrets and unnecessary files from ever being tracked.

**Stage and commit**

Stage all project files with `git add .` and create the initial commit with a clear message describing the project.

**Connect to GitHub and push**

Create a new repository on GitHub. Copy the remote URL. Add it as the origin remote using `git remote add origin`. Rename the default branch to `main` and push the code using `git push -u origin main`.

**Handling secret detection errors**

If GitHub rejects a push because a secret was detected, do not simply remove the key from the latest file. The secret still lives in a previous commit in the Git history. Use BFG Repo Cleaner or an interactive rebase to purge it from history, then force-push the cleaned history. Only then will GitHub accept the push.

---

## Key Features

- End-to-end multi-cloud data migration from AWS to Azure
- SQL to NoSQL data transformation with full type safety
- Paginated scanning of DynamoDB for handling large datasets
- Secure credential management using environment variables only
- Upsert logic preventing duplicate entries across repeated runs
- LAMP-style web application for real-time data ingestion and testing

---

## Learning Outcomes

- Hands-on experience provisioning and configuring cloud infrastructure on both AWS and Azure
- Understanding of relational-to-NoSQL data modeling and migration strategies
- Practical application of AWS IAM users, roles, policies, and CLI tooling
- Cross-cloud architecture design and trade-off analysis between AWS and Azure services
- Debugging real-world deployment issues including credential exposure, data type mismatches, and pagination edge cases

---

## Future Enhancements

- Automate the full pipeline using AWS Lambda triggered by CloudWatch Events or a cron job on EC2
- Implement an Azure Data Factory pipeline as a managed, no-code alternative migration path
- Add a CI/CD pipeline using GitHub Actions to validate and trigger migration scripts on every push
- Build a unified monitoring dashboard using AWS CloudWatch and Azure Monitor with cross-cloud alerting
- Containerize the migration scripts using Docker for consistent, reproducible execution across environments
- Add schema validation and data quality checks at each stage before writing to the target database
- Implement dead-letter logging to capture failed records and support selective retry without full re-runs
- Extend the pipeline to support bidirectional sync between AWS and Azure for active-active or disaster recovery scenarios

---

> Built by Shivam | Cloud & DevOps Engineer | [GitHub](https://github.com/your-username) | [LinkedIn](https://linkedin.com/company/cloudbuild-technologies/)
