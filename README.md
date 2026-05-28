# Repository Branches

This repository is maintained with **two distinct branches**, each targeting a different environment and deployment workflow.

---

# `main` Branch — Local Development

The `main` branch is intended for **local development and testing** using Docker and Apache Airflow running on your host machine.

In this setup:

* Airflow runs locally through Docker Compose
* Data is read from and written to an Amazon S3 bucket
* AWS credentials are configured locally through a `.env` file

## AWS Credentials

To allow local services to access S3, you must configure your AWS credentials inside a `.env` file.

Example:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## Security Recommendations

Sensitive files should **never** be committed to the repository.

Make sure the following files are included in both `.gitignore` and `.dockerignore`:

```gitignore
.env
```

---

# `dev-prod` Branch — Production Environment

The `dev-prod` branch contains the **production-ready infrastructure and deployment pipeline**.

This branch uses:

* Amazon ECS
* Amazon ECR
* GitHub Actions CI/CD
* OIDC authentication with AWS
* Automated task definition updates

Unlike the `main` branch, this environment does **not** rely on static AWS credentials.

---

# CI/CD Pipelines

## `main` Branch CI/CD

The CI/CD pipeline for `main`:

1. Builds the Docker image
2. Pushes the image to Docker Hub

### Required GitHub Secrets

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

---

## `dev-prod` Branch CI/CD

The CI/CD pipeline for `dev-prod`:

1. Builds the Docker image
2. Pushes the image to Amazon ECR
3. Updates ECS task definitions
4. Deploys new container versions automatically

This pipeline authenticates with AWS using **OIDC**.

### Required GitHub Secrets / Variables

```text
AWS_REGION
AWS_ARN_ROLE
```

* `AWS_REGION`: AWS region where the infrastructure is deployed
* `AWS_ARN_ROLE`: IAM Role ARN assumed by GitHub Actions through OIDC

---

# ECS / Airflow Environment Variables

The production Airflow containers require additional ECS networking variables:

```text
ECS_TARGET_SUBNETS
ECS_TARGET_SECURITY_GROUPS
```

These values define:

* The ECS subnets used by the tasks
* The security groups attached to the tasks

---

# Infrastructure as Code (IaC)

Infrastructure definitions, task definitions, and environment injection configuration are available in the IaC repository:

[Pipeout IaC Repository][(https://github.com/Pipeout/IaC?utm_source=chatgpt.com)](https://github.com/Pipeout/IaC/blob/main/ecs_task_definitions.tf)

---

# Notes

* The `main` branch is optimized for rapid local iteration and debugging.
* The `dev-prod` branch is optimized for automated cloud deployment and production execution.
* Environment variables injected into production containers are defined directly in ECS task definitions.
