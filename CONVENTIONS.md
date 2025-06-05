# Project Development Conventions
AI-generated, reviewed by me.
## 1. Introduction

This document outlines the development conventions for the Aurora backend. Adhering to these conventions will help maintain code quality, consistency, improve collaboration, and ensure the scalability and maintainability of the project. This is a living document and may be updated as the project evolves.

## 2. General Principles

* **Clarity & Predictability:** Names and structures should be easy to understand and predict.
* **Consistency:** Apply chosen patterns uniformly across all resources, files, and code.
* **Scalability:** Conventions should accommodate growth in services, features, environments, and regions.
* **Conciseness (Balanced with Clarity):** Aim for reasonably short names, but not at the expense of clarity.
* **Machine Readability:** Use characters friendly to automation scripts and AWS (lowercase alphanumeric, hyphens).
* **Tagging as a First-Class Citizen:** Tags are crucial for cost management, automation, security, and organization.
* **Domain-Driven Structure:** Organize infrastructure and code by business domains/capabilities.

## 3. Project Folder & File Structure

The project adopts a domain-driven structure to enhance clarity and organization.
This is the full proposed structure. It will grow according to actual project needs.

```
AuroraAssistant/
├── .github/                    # CI/CD workflows
├── .gitignore
├── README.MD                   # Project overview, setup, etc.
├── CONVENTIONS.MD              # This file
├── docs/                       # Architectural diagrams, detailed explanations
│   └── architecture/
│       ├── overview.md
│       └── <domain_name>_diagram.md
│
├── iac/                        # Infrastructure as Code (Terraform)
│   ├── domains/                # Domain-specific infrastructure compositions
│   │   ├── <domain_1>/         # e.g., user_interaction, agent_orchestration
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── <specific_resource_group>.tf
│   │   └── <domain_2>/
│   ├── modules/                # Generic, reusable Terraform modules (service-level)
│   │   ├── aws_lambda_function/
│   │   ├── aws_api_gateway_v2/
│   │   └── ...
│   ├── environments/           # Environment-specific configurations (dev, stg, prd)
│   │   ├── dev/
│   │   │   ├── main.tf         # Instantiates domain compositions
│   │   │   ├── terraform.tfvars
│   │   │   └── backend.tf      # Terraform backend configuration
│   │   └── ...
│   └── global/                 # Global AWS resources (e.g., central IAM users)
│
├── src/                        # Application source code
│   ├── domains/
│   │   ├── <domain_1>/         # e.g., user_interaction
│   │   │   ├── api_handlers/
│   │   │   │   └── <handler_name_lambda>/
│   │   │   │       ├── app.py
│   │   │   │       └── requirements.txt
│   │   │   └── ...
│   │   ├── <domain_2>/         # e.g., ai_tooling
│   │   │   ├── <tool_name_handler>/
│   │   │   │   ├── app.py
│   │   │   │   ├── requirements.txt
│   │   │   │   └── openapi_schema.json # OpenAPI schema for this tool
│   │   │   └── ...
│   │   └── common_libs/        # Shared utilities across domains
│
├── scripts/                    # Helper scripts (deployment, testing, etc.)
└── tests/                      # Automated tests
    ├── unit/
    │   └── domains/            # Unit tests mirroring src/domains structure
    │       ├── <domain_1>/
    │       └── ...
    └── integration/
        └── ...
```

## 4. AWS Resource Naming Convention

All AWS resources should follow this pattern:

**`<app_name>-<environment>-<domain_shortcode>-<aws_service_shortcode>-<component_description>-<optional_suffix>`**

* **`<app_name>`**: aurora
* **`<environment>`**: Environment identifier.
    * `dev`: Development
    * `stg`: Staging
    * `prd`: Production
    * `qa`: Quality Assurance
* **`<domain_shortcode>`**: Short code for the business domain. Examples:
    * `ui`: User Interaction (e.g., API gateways, initial handlers)
    * `ao`: Agent Orchestration (e.g., core Bedrock agents, supervising logic)
    * `ait`: AI Tooling (e.g., Lambdas serving as Bedrock agent tools)
    * `km`: Knowledge Management (e.g., S3 for KBs, ingestion pipelines)
    * `sec`: Security (e.g., specific IAM roles for cross-domain security functions)
    * `data`: Data Persistence (e.g., DynamoDB tables, RDS instances)
    * *(Define additional domain shortcodes as your project evolves)*
* **`<aws_service_shortcode>`**: Abbreviation for the AWS service. Examples:
    * `agw`: API Gateway
    * `lambda`: Lambda Function
    * `iam`: IAM Role/Policy
    * `s3`: S3 Bucket
    * `agent`: Bedrock Agent
    * `agrp`: Bedrock Action Group (for the TF resource name; the logical name in Bedrock might be simpler)
    * `kb`: Bedrock Knowledge Base
    * `cwlg`: CloudWatch Log Group
    * `ddb`: DynamoDB Table
    * `sqs`: SQS Queue
    * `sns`: SNS Topic
* **`<component_description>`**: Hyphenated, descriptive name of the specific resource's purpose (e.g., `user-auth`, `task-orchestrator`, `main-public-api`, `order-processing-tool`).
* **`<optional_suffix>`**: Clarifier if needed (e.g., `role`, `policy`, `api`, `func`, `bucket`, `table`, `v1`, `canary`). Often indicates the type if not clear from `aws_service_shortcode`.

**Examples:**

* Lambda (API Handler): `aurora-dev-ui-lambda-user-request-handler`
* Lambda (Agent Tool): `aurora-dev-ait-lambda-calendar-tool`
* IAM Role: `aurora-prd-ait-iam-calendar-tool-lambda-exec-role`
* Bedrock Agent: `aurora-stg-ao-agent-customer-support`
* S3 Bucket (KB Source): `aurora-prd-km-s3-policy-docs-kb-source` (Note: S3 names are global)

## 5. AWS Tagging Strategy

All taggable AWS resources **MUST** have the following tags. Tag keys should be `lowercase-with-hyphens`.

**Mandatory Tags:**

* `Name`: Human-readable name, often identical to the resource name.
* `environment`: `dev | stg | prd | qa`.
* `domain`: The business domain this resource belongs to (e.g., `user-interaction`, `ai-tooling`, `agent-orchestration`).
* `managed-by`: `terraform` (or `cloudformation`, `manual` if unavoidable).

## 6. Terraform Conventions

* **Structure:**
    * Generic, reusable modules reside in `iac/modules/`.
    * Domain-specific compositions reside in `iac/domains/`, calling generic modules.
    * Environment configurations in `iac/environments/` instantiate domain compositions.
* **Naming:**
    * Module source names: `lowercase_with_underscores`.
    * Local module instance names: `lowercase_with_underscores`, descriptive (e.g., `module "user_api_gateway" { ... }`).
    * Resource local names: `lowercase_with_underscores`, descriptive (e.g., `resource "aws_lambda_function" "calendar_tool_lambda" { ... }`).
    * Variable names: `snake_case`.
    * Output names: `snake_case`.
* **Variables:**
    * Declare all variables in `variables.tf` with `description` and `type`.
    * Provide `default` values for optional variables.
    * Use `.tfvars` files (e.g., `terraform.tfvars`, `dev.auto.tfvars`) for environment-specific values. Do not commit sensitive data in `.tfvars` files to version control; use secure methods like environment variables during CI/CD or dedicated secret management.
* **Formatting:** Use `terraform fmt` to ensure consistent formatting.
* **Comments:** Use `#` for single-line comments and `/* ... */` for multi-line comments to explain complex logic or non-obvious configurations.
* **Modules:** Strive for small, focused modules. Outputs should expose necessary attributes for other modules or root configurations.

## 7. Source Code Conventions (Example: Python for Lambdas)

* **Style Guide:** Adhere to PEP 8 for Python. Use linters (e.g., Flake8, Pylint) and formatters (e.g., Black, autopep8).
* **Structure:** Code for each Lambda function should reside in its own directory within `src/domains/<domain_name>/<handler_or_component_name>/`.
    * Include `app.py` (or similar main handler file) and `requirements.txt`.
* **Naming:**
    * Files: `snake_case.py`.
    * Functions & Variables: `snake_case`.
    * Classes: `PascalCase`.
    * Constants: `UPPER_SNAKE_CASE`.
* **Error Handling:** Implement robust error handling. Return meaningful error messages and status codes.
* **Logging:** Use structured logging (e.g., JSON format). Leverage AWS Lambda Powertools for Python for logging, metrics, and tracing. Include context (e.g., request ID, domain, component).
* **Configuration:** Pass configuration to Lambdas via environment variables. Do not hardcode environment-specific values. Use AWS Systems Manager Parameter Store or AWS Secrets Manager for sensitive data.
* **Dependencies:** Manage dependencies using `requirements.txt` for Python. Keep dependencies minimal.

## 8. API Design Conventions (OpenAPI for Bedrock Action Groups)

* **Specification:** Use OpenAPI 3.0.x.
* **Clarity:**
    * Provide a clear `summary` and `description` for each path and operation.
    * Use a meaningful and consistent `operationId`.
* **Schemas:**
    * Define clear request and response schemas.
    * Use descriptive property names.
    * Specify data types accurately.
    * Mark `required` fields.
* **Examples:** Include `examples` for request and response payloads where helpful.
* **File Naming & Location:** Store OpenAPI schemas as `openapi_schema.json` co-located with the Lambda tool handler code it describes (e.g., `src/domains/ai_tooling/<tool_name_handler>/openapi_schema.json`).
* **Simplicity for Bedrock:** Remember Bedrock agents work best with clear, unambiguous descriptions and straightforward API structures. Avoid overly complex or deeply nested structures if possible.

## 9. Commit Message Conventions

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This helps in generating changelogs and makes commit history more readable.

Format: `<type>(<scope>): <subject>`

* **`<type>`:** `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style` (formatting), `refactor`, `test`, `chore` (build/tooling changes), `perf` (performance improvements), `ci`, `build`.
* **`<scope>` (optional):** The part of the project affected (e.g., `ait`, `ui-api`, `terraform-lambda-module`, `docs-readme`).
* **`<subject>`:** Concise description of the change in present tense.

**Examples:**

* `feat(ait): implement calendar event creation tool`
* `fix(ui): correct error handling for invalid user input`
* `docs(conventions): update resource naming for bedrock agents`
* `chore(iac): upgrade terraform aws provider to v5.x`

## 10. Branching Strategy

A Gitflow-like branching model is recommended:

* **`main` (or `master`):** Represents production-ready code. Merges to `main` should trigger production deployments.
* **`develop`:** Integration branch for ongoing development. New features are merged here.
* **`feature/<feature-name>`:** Branched from `develop` for new features or tasks (e.g., `feature/bedrock-order-tool`). Merge back into `develop` via Pull Request.
* **`hotfix/<fix-name>`:** Branched from `main` for critical production fixes. Merged into both `main` and `develop`.
* **`release/<version>`:** (Optional) For preparing a new production release (final testing, version bumping).

## 11. Documentation

* **`README.MD`:** High-level project overview, setup, and quick start.
* **`CONVENTIONS.MD` (this file):** Detailed development standards.
* **`docs/architecture/`:** In-depth architectural diagrams (using tools like diagrams.net/draw.io, Mermaid, or C4 model) and explanations for different domains and the overall system.
* **Inline Code Comments:** Explain complex, non-obvious, or critical sections of code.
* **Terraform Descriptions:** All variables and outputs in Terraform should have clear `description` attributes.

## 12. Review and Updates

These conventions are intended to evolve with the project. Suggestions for improvements are welcome. Changes to these conventions should be discussed with the team and updated in this document via a Pull Request.
