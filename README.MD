# 🚀 Automated Python CI/CD Pipeline using Jenkins + GitHub Actions

## 📌 Project Overview

This project demonstrates a **fully automated CI/CD pipeline for a Python (Flask) application** using **Jenkins triggered by GitHub Actions**.

The key idea behind this project is automation.

Whenever a developer **pushes code to GitHub**, a **GitHub Actions workflow automatically triggers a Jenkins pipeline**. Jenkins then builds and deploys the application to the server **without any manual clicks or intervention**.

This setup removes the need to manually start Jenkins jobs. The entire pipeline runs automatically using a **YAML workflow file and Jenkins remote trigger API**.

This project represents a **real-world DevOps workflow used in production environments**.

---
# Architecture Diagram
![jenkins](jen/d1.png)
# Tech Stack

| Technology | Purpose |
|------------|--------|
| Python | Backend Application |
| Flask | Web Framework |
| Jenkins | CI/CD Pipeline Automation |
| GitHub | Source Code Management |
| GitHub Actions | Workflow Automation |
| Git | Version Control |
| AWS EC2 | Jenkins & Application Hosting |
| Linux | Server Environment |
| SSH | Secure Authentication |
| Curl API | Trigger Jenkins Job |

---
![jenkins](jen/ds2.png)
# ⚡ Key Features

- Fully automated CI/CD pipeline
- Jenkins pipeline triggered automatically
- GitHub Actions workflow automation
- No manual Jenkins build required
- Secure Jenkins remote trigger using token
- Private GitHub repository integration
- AWS EC2 deployment
- SSH authentication configured
- Automatic build and deployment

---

# 🏗 CI/CD Architecture

```
Developer
   │
   │ Push Code
   ▼
GitHub Repository
   │
   │ Trigger Workflow
   ▼
GitHub Actions
   │
   │ API Request (curl)
   ▼
Jenkins Server (AWS EC2)
   │
   │ Pipeline Execution
   ▼
Build + Install Dependencies
   │
   ▼
Deploy Python Application
   │
   ▼
Live Server 🚀
```

---

# 📂 Project Structure

```
Email-Python-CICD-GitHub-Action
│
├── .github
│   └── workflows
│       └── jenkins-action.yml
│
├── templates
│
├── app.py
├── requirements.txt
├── Dockerfile
├── jenkinsfile
└── README.md
```

---

# ⚙️ How It Works

## Step 1 — Developer Pushes Code

A developer pushes code to the GitHub repository.

```
git add .
git commit -m "update"
git push origin master
```
![jenkins](jen/ds2.png)


---

## Step 2 — GitHub Actions Workflow Triggers

```
📸 Screenshot
```
![jenkins](jen/api.png)
GitHub automatically detects the push event and runs the workflow file.

Workflow location:

```
.github/workflows/jenkins-action.yml
```

Example workflow configuration:

```yaml
name: Trigger Jenkins Pipeline

on:
  push:
    branches:
      - master

jobs:
  trigger-jenkins:
    runs-on: ubuntu-latest

    steps:
      - name: Trigger Jenkins Job
        run: |
          curl -X POST http://YOUR_JENKINS_IP:8080/job/email/build?token=jenkins-token
```

![jenkins](jen/git.png)

## Step 3 — GitHub Actions Sends Request to Jenkins

GitHub Actions uses **curl API** to send a **POST request** to Jenkins.

This triggers the Jenkins pipeline automatically.
![jenkins](appi/.png)
![jenkins](appi2/.png)

---

## Step 4 — Jenkins Pipeline Executes

Jenkins receives the trigger and starts executing the pipeline.

Pipeline tasks include:

- Cloning repository
- Installing dependencies
- Running Python application
- Deploying the application



---

## Step 5 — Application Deployment

After successful pipeline execution, the application is deployed on the server automatically.

📸 Screenshot

```
![jenkins](jen/j5.png)
```

---

# 🔐 Jenkins Configuration

## Create Jenkins Job

1. Install Jenkins on AWS EC2
2. Open Jenkins Dashboard
3. Create a new Pipeline Job

📸 Screenshot

```
![jenkins](jen/jen2.png)
```

---

## Enable Remote Trigger

Inside Jenkins job configuration:

```
Build Triggers
✔ Trigger builds remotely
Token: jenkins-token
```

This token allows GitHub Actions to trigger Jenkins securely.

📸 Screenshot

```
![jenkins](jen/jen.png)
```

---

# 🔑 Credentials Configuration

Since the repository is **private**, Jenkins requires authentication.

Configured inside **Jenkins Credential Manager**.

Credentials used:

- GitHub Repository Token
- SSH Private Key Authentication

📸 Screenshot

```
![jenkins](jen/api2.png)
![jenkins](jen/token.png)
``

```
for Result 
```

![jenkins](jen/result.png)
![jenkins](jen/r1.png)
![jenkins](jen/r2.png)
![jenkins](jen/j5.png)
---

# 📈 Pipeline Result

After configuration:

1. Developer pushes code
2. GitHub Actions workflow starts
3. Jenkins pipeline triggers automatically
4. Application builds
5. Application deploys to server
6. Live server updates automatically

This creates a **complete automated CI/CD pipeline**.

---

# 🎯 Learning Outcomes

- CI/CD pipeline automation
- Jenkins pipeline configuration
- GitHub Actions workflow setup
- Jenkins remote trigger API
- Secure credentials management
- AWS EC2 deployment
- DevOps automation practices

---

# 👨‍💻 Author

**Shivam Garud**

DevOps Engineer  
Cloud & Automation Enthusiast

---

# ⭐ Support

If you found this project useful:

⭐ Star the repository  
🍴 Fork the project  
📢 Share with the DevOps community
