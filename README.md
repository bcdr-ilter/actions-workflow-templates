# Configuration-Driven CI/CD Templates

This repository contains reusable CI/CD templates that use configuration files instead of hardcoded branch logic.

## Overview

Instead of maintaining hardcoded branch conditions in your CI/CD pipelines, this system uses a single `branch-config.yml` file to define environment-specific settings. This approach provides:

- **Centralized Configuration**: All branch-specific settings in one place
- **Easy Maintenance**: Add new branches or modify environments without touching pipeline code
- **Consistency**: Same configuration logic across Jenkins and GitHub Actions
- **Flexibility**: Support for variable substitution and overrides

## Configuration File Structure

The `branch-config.yml` file uses **Jinja2 templating** to define environment variables for different branches:

```yaml
branches:
  main:
    input_bucket_name: "invent-{{ customer_name }}-input"
    output_bucket_name: "invent-{{ customer_name }}-output"
    datastore_bucket_name: "invent-{{ customer_name }}-{% if customer_environment == 'prod-us' %}wba{% else %}wba{% endif %}-datastore"
    pokedex_environment: "{% if customer_environment.startswith('prod') %}wba{% else %}dev{% endif %}"
    log_level: "{% if customer_environment == 'prod-us' %}INFO{% else %}DEBUG{% endif %}"
    resource_limits:
      cpu: "{% if customer_environment.startswith('prod') %}4{% else %}2{% endif %}"
      memory: "{% if customer_environment.startswith('prod') %}8Gi{% else %}4Gi{% endif %}"
    
  dev:
    input_bucket_name: "invent-{{ customer_name }}-input-dev"
    # ... other configuration
    
  # Pattern matching for feature branches
  "feature-*":
    input_bucket_name: "invent-{{ customer_name }}-input-{{ branch_name | replace('feature-', '') }}"
    # ... other configuration

default:
  # Configuration for branches not explicitly defined
  input_bucket_name: "invent-{{ customer_name }}-input-dev"
  customer_subdomain: "{% if customer_environment == 'dev' %}dev{% else %}customertest{% endif %}"
  # ... other configuration
```

### Jinja2 Templating Features

The configuration supports powerful **Jinja2 templating** with these features:

#### Basic Variables
- `{{ customer_name }}` - Customer name (automatically lowercased)
- `{{ branch_name }}` - Current branch name
- `{{ customer_subdomain }}` - Customer subdomain from repository variables
- `{{ customer_environment }}` - Customer environment from repository variables
- `{{ cloud_provider }}` - Cloud provider (aws/azure)

#### Helper Functions
- `{{ is_main_branch() }}` - Returns true if current branch is 'main'
- `{{ is_dev_branch() }}` - Returns true if current branch is 'dev'
- `{{ is_feature_branch() }}` - Returns true if branch starts with 'feature'
- `{{ get_secret_env() }}` - Returns 'prod' for main branch, 'dev' for others

#### Conditional Logic
```yaml
pokedex_environment: "{% if customer_environment.startswith('prod') %}wba{% else %}dev{% endif %}"
log_level: "{% if is_main_branch() %}INFO{% else %}DEBUG{% endif %}"
monitoring_enabled: "{% if customer_environment.startswith('prod') %}true{% else %}false{% endif %}"
```

#### Filters
```yaml
# String manipulation
input_bucket_name: "invent-{{ customer_name }}-input-{{ branch_name | replace('feature-', '') }}"
namespace: "{{ customer_name | upper }}-{{ branch_name | lower }}"

# Default values
customer_subdomain: "{{ customer_subdomain if customer_subdomain else 'prod' }}"
```

#### Complex Data Structures
```yaml
resource_limits:
  cpu: "{% if customer_environment.startswith('prod') %}4{% else %}2{% endif %}"
  memory: "{% if customer_environment.startswith('prod') %}8Gi{% else %}4Gi{% endif %}"
  
allowed_ips:
  - "10.0.0.0/8"
  - "172.16.0.0/12"
  - "192.168.0.0/16"
```

### Configuration Options

Each branch configuration supports these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `input_bucket_name` | Input data bucket name | `invent-acme-input` |
| `output_bucket_name` | Output data bucket name | `invent-acme-output` |
| `datastore_bucket_name` | Datastore bucket name | `invent-acme-datastore` |
| `maps_database_secret_id` | Database secret identifier | `acme-prod-app` |
| `pokedex_environment` | Pokedex environment setting | `prod`, `dev`, `wba` |
| `rocks_env` | Rocks environment setting | `prod`, `dev`, `{branch_name}` |
| `k8s_namespace` | Kubernetes namespace | `{customer_name}`, `{customer_name}-{branch_name}` |
| `image_env` | Docker image environment | `prod`, `dev` |
| `customer_subdomain` | Customer subdomain | `prod`, `dev`, `customertest` |

## Implementation Options

We provide **three different approaches** for implementing configuration-driven CI/CD, each with different trade-offs:

### 🏆 **Option 1: Composite Action (Recommended)**
**Best for: Most use cases - Clean, maintainable, and efficient**

```yaml
- name: Process Branch Configuration
  uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
  with:
    branch-name: ${{ github.head_ref || github.ref_name }}
    customer-name: ${{ vars.CUSTOMER_NAME }}
    customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
    # ... other parameters
```

**Architecture:**
- `action.yml` - Clean composite action definition
- `process_config.py` - Dedicated Python script with full Jinja2 support
- Uses `${{ github.action_path }}` to reference the Python file

✅ **Pros:**
- **Full Jinja2 Support**: Complete templating with conditionals, filters, and helper functions
- **Clean Architecture**: Separate Python file for maintainability
- **Single line to use**: Just one step in your workflow
- **No additional checkouts**: Self-contained action
- **Automatic fallbacks**: Creates default config if missing
- **Beautiful debug output**: Emoji-rich logging

❌ **Cons:**
- Requires referencing this template repository

### 🔧 **Option 2: Standalone Shell Script**
**Best for: Teams who want complete independence from template repos**

Uses only shell scripting with `yq` - completely self-contained in each repository.

✅ **Pros:**
- No external dependencies
- Completely self-contained
- Uses only GitHub runner built-in tools
- Fast execution

❌ **Cons:**
- More complex workflow file
- Less powerful templating than Jinja2
- Harder to maintain across repositories

### 🐍 **Option 3: Checkout Template + Python**
**Best for: Teams needing full Jinja2 power and complex templating**

Checks out this template repository and uses the full Python-based processor.

✅ **Pros:**
- Full Jinja2 templating power
- Most flexible and powerful
- Support for complex conditionals and filters

❌ **Cons:**
- Requires additional repository checkout
- Python dependencies to install
- Slower execution

## How to Use

### Quick Start: Copy a Ready-to-Use Pipeline

We provide ready-to-use CI/CD pipeline files that you can copy to your repository:

#### 1. **Simple Pipeline** (Recommended for most users)
Copy `.github/workflows/simple-deploy.yml` to your repository:

```yaml
name: Simple Deploy

on:
  push:
    branches: [ main, dev ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Process Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.ref_name }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
          customer-subdomain: ${{ vars.CUSTOMER_SUBDOMAIN }}
          cloud-provider: ${{ vars.CLOUD_PROVIDER }}

      - name: Build and Deploy
        run: |
          echo "🚀 Deploying to $K8S_NAMESPACE"
          # Your deployment commands here
          # All configuration variables are available!
```

#### 2. **Full-Featured Pipeline** (For complex deployments)
Copy `.github/workflows/deploy-application.yml` for a complete CI/CD pipeline with:
- ✅ Multi-stage builds (configure → build → test → deploy)
- ✅ Multi-cloud support (AWS + Azure)
- ✅ Kubernetes deployment
- ✅ Storage bucket configuration
- ✅ Feature branch cleanup
- ✅ Post-deployment verification
- ✅ Beautiful GitHub summaries

### Option 1: Using Composite Action (Recommended)

1. **Use the composite action in your workflow:**

```yaml
name: Deploy Application

on:
  push:
    branches: [ main, dev ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Process Branch Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.head_ref || github.ref_name }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
          customer-subdomain: ${{ vars.CUSTOMER_SUBDOMAIN }}
          cloud-provider: ${{ vars.CLOUD_PROVIDER }}
          # Optional overrides
          input-bucket-name: ${{ vars.INPUT_BUCKET_NAME }}

      # Your deployment steps here - all environment variables are now set!
      - name: Deploy
        run: echo "Deploying to $K8S_NAMESPACE with bucket $INPUT_BUCKET_NAME"
```

2. **Optionally create a custom `branch-config.yml`** in your repository root (the action will create a sensible default if none exists)

### Option 2: Using Standalone Workflow

Copy `.github/workflows/airflow-deploy-standalone.yml` to your repository and customize as needed.

### Option 3: Using Python Processor

Copy `.github/workflows/airflow-deploy.yml` to your repository.

### 1. Create Configuration File

Create a `branch-config.yml` file in your repository root with your branch-specific settings:

```yaml
branches:
  main:
    input_bucket_name: "invent-{{ customer_name }}-input"
    output_bucket_name: "invent-{{ customer_name }}-output"
    datastore_bucket_name: "invent-{{ customer_name }}-datastore"
    pokedex_environment: "{% if customer_environment.startswith('prod') %}wba{% else %}prod{% endif %}"
    rocks_env: "prod"
    k8s_namespace: "{{ customer_name }}"
    image_env: "prod"
    customer_subdomain: "{{ customer_subdomain if customer_subdomain else 'prod' }}"
    log_level: "{% if customer_environment == 'prod-us' %}INFO{% else %}DEBUG{% endif %}"
    resource_limits:
      cpu: "{% if customer_environment.startswith('prod') %}4{% else %}2{% endif %}"
      memory: "{% if customer_environment.startswith('prod') %}8Gi{% else %}4Gi{% endif %}"
    
  dev:
    input_bucket_name: "invent-{{ customer_name }}-input-dev"
    output_bucket_name: "invent-{{ customer_name }}-output-dev"
    datastore_bucket_name: "invent-{{ customer_name }}-datastore-dev"
    pokedex_environment: "dev"
    rocks_env: "dev"
    k8s_namespace: "{{ customer_name }}-{{ branch_name }}"
    image_env: "dev"
    customer_subdomain: "dev"
    log_level: "DEBUG"
    resource_limits:
      cpu: "1"
      memory: "2Gi"
  
  # Pattern matching for feature branches
  "feature-*":
    input_bucket_name: "invent-{{ customer_name }}-input-{{ branch_name | replace('feature-', '') }}"
    output_bucket_name: "invent-{{ customer_name }}-output-{{ branch_name | replace('feature-', '') }}"
    datastore_bucket_name: "invent-{{ customer_name }}-datastore-dev"
    pokedex_environment: "dev"
    rocks_env: "{{ branch_name }}"
    k8s_namespace: "{{ customer_name }}-{{ branch_name }}"
    image_env: "dev"
    customer_subdomain: "{% if customer_environment == 'dev' %}dev{% else %}customertest{% endif %}"
    log_level: "DEBUG"
    resource_limits:
      cpu: "1"
      memory: "2Gi"

default:
  input_bucket_name: "invent-{{ customer_name }}-input-dev"
  output_bucket_name: "invent-{{ customer_name }}-output-dev"
  datastore_bucket_name: "invent-{{ customer_name }}-datastore-dev"
  pokedex_environment: "dev"
  rocks_env: "{{ branch_name }}"
  k8s_namespace: "{{ customer_name }}-{{ branch_name }}"
  image_env: "dev"
  customer_subdomain: "{% if customer_environment == 'dev' %}dev{% else %}customertest{% endif %}"
  log_level: "DEBUG"
  resource_limits:
    cpu: "1"
    memory: "2Gi"

# Global configuration that applies to all branches
global:
  monitoring_enabled: "{% if customer_environment.startswith('prod') %}true{% else %}false{% endif %}"
  backup_retention_days: "{% if customer_environment.startswith('prod') %}30{% else %}7{% endif %}"
  storage_class: "{% if cloud_provider == 'aws' %}gp3{% else %}Premium_LRS{% endif %}"
  
  # 🔐 Cloud-specific configuration using environment variables
  azure:
    subscription_id: "{% if customer_environment == 'prod-us' %}{{ env.AZURE_SUBSCRIPTION_ID_PROD_US }}{% elif customer_environment == 'prod-eu' %}{{ env.AZURE_SUBSCRIPTION_ID_PROD_EU }}{% else %}{{ env.AZURE_SUBSCRIPTION_ID_DEV }}{% endif %}"
    databricks_client_id: "{{ env.AZURE_DATABRICKS_CLIENT_ID }}"
    tenant_id: "{{ env.AZURE_TENANT_ID }}"
    storage_account_name: "{{ env.STORAGE_ACCOUNT_NAME }}"
    storage_account_access_key: "{{ env.STORAGE_ACCOUNT_ACCESS_KEY }}"
  
  aws:
    region: "{{ env.AWS_REGION | default('us-east-1') }}"
    
  # 🔐 Application secrets (configurable per environment)
  secrets:
    fernet_key: "{{ env.FERNET_KEY }}"
    sentry_dsn: "{{ env.SENTRY_DSN }}"
    postgres_username: "{{ env.POSTGRES_CREDENTIALS_USR }}"
    postgres_password: "{{ env.POSTGRES_CREDENTIALS_PSW }}"
    github_token: "{{ env.GH_PAT }}"
```

### 2. Repository Variables

Set up these repository variables in your GitHub repository settings:

- `CUSTOMER_NAME` - Your customer name (e.g., "AcmeCorp")
- `CUSTOMER_ENVIRONMENT` - Your environment (e.g., "prod-eu", "dev")
- `CUSTOMER_SUBDOMAIN` - Your subdomain (e.g., "prod", "dev")
- `CLOUD_PROVIDER` - Cloud provider ("aws" or "azure")
- `AIRFLOW_VERSION` - Airflow version (e.g., "2.4.2")

Optional override variables (if you want to override config file values):
- `INPUT_BUCKET_NAME`
- `OUTPUT_BUCKET_NAME`
- `DATASTORE_BUCKET_NAME`
- `MAPS_DATABASE_SECRET_ID`

### 3. Available Environment Variables

After running the composite action, these environment variables are available in your workflow:

| Variable | Description | Example |
|----------|-------------|---------|
| `INPUT_BUCKET_NAME` | Input storage bucket | `invent-wba-input` |
| `OUTPUT_BUCKET_NAME` | Output storage bucket | `invent-wba-output` |
| `DATASTORE_BUCKET_NAME` | Datastore bucket | `invent-wba-datastore` |
| `MAPS_DATABASE_SECRET_ID` | Database secret identifier | `wba-prod-app` |
| `POKEDEX_ENVIRONMENT` | Pokedex environment | `wba`, `dev` |
| `ROCKS_ENV` | Rocks environment | `prod`, `dev` |
| `K8S_NAMESPACE` | Kubernetes namespace | `wba`, `wba-dev` |
| `IMAGE_ENV` | Image environment | `prod`, `dev` |
| `K8S_CLUSTER` | Kubernetes cluster name | `prod-eu`, `dev` |
| `K8S_CLUSTER_RG` | Kubernetes resource group | `prod-eu-rg` |
| `CUSTOMER_SUBDOMAIN` | Customer subdomain | `prod`, `dev` |
| `LOG_LEVEL` | Application log level | `INFO`, `DEBUG` |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | `12345678-1234-...` |
| `AZURE_DATABRICKS_CLIENT_ID` | Azure Databricks client | `87654321-4321-...` |
| `AZURE_TENANT_ID` | Azure tenant ID | `abcdef12-3456-...` |
| `STORAGE_ACCOUNT_NAME` | Azure storage account | `mystorageaccount` |
| `AWS_REGION` | AWS region | `us-east-1`, `eu-west-1` |
| `FERNET_KEY` | Airflow encryption key | `encrypted-key-value` |
| `SENTRY_DSN` | Sentry error tracking | `https://...@sentry.io/...` |
| `POSTGRES_USERNAME` | Database username | `admin` |
| `POSTGRES_PASSWORD` | Database password | `password123` |

You can use these variables in any subsequent step:

```yaml
- name: Deploy Application
  run: |
    echo "Deploying to namespace: $K8S_NAMESPACE"
    kubectl apply -f manifests/ -n $K8S_NAMESPACE
    
    echo "Using input bucket: $INPUT_BUCKET_NAME"
    aws s3 sync ./data s3://$INPUT_BUCKET_NAME/
```

### 4. Repository Secrets

Set up these repository secrets:

#### Core Secrets (Required)
- `AZURE_CREDENTIALS` - Azure service principal credentials (JSON format)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key  
- `FERNET_KEY` - Encryption key for Airflow
- `SENTRY_DSN` - Sentry error tracking DSN

#### Database Secrets
- `POSTGRES_CREDENTIALS_USR` - PostgreSQL username
- `POSTGRES_CREDENTIALS_PSW` - PostgreSQL password

#### Azure-Specific Secrets
- `AZURE_DATABRICKS_CLIENT_ID` - Azure Databricks client ID
- `STORAGE_ACCOUNT_ACCESS_KEY` - Azure Storage account access key

#### Additional Variables for Azure Multi-Environment
- `AZURE_SUBSCRIPTION_ID_PROD_US` - Azure subscription for US production
- `AZURE_SUBSCRIPTION_ID_PROD_EU` - Azure subscription for EU production  
- `AZURE_SUBSCRIPTION_ID_DEV` - Azure subscription for development
- `AZURE_TENANT_ID` - Azure tenant ID
- `STORAGE_ACCOUNT_NAME` - Azure storage account name

#### Repository Access
- `GH_PAT` - GitHub Personal Access Token (for accessing private repos)

**Example Azure Credentials Format:**
```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret", 
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}
```

### 4. Use the Workflow

Reference the `airflow-deploy.yml` workflow in your repository:

```yaml
name: Deploy Application

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    uses: ./.github/workflows/airflow-deploy.yml
    with:
      airflow-image-version: "latest"
    secrets: inherit
```

## Jenkins Integration

To use the same configuration system in Jenkins, you can modify your Jenkinsfile to read the YAML configuration:

```groovy
// At the top of your Jenkinsfile
@Library('your-shared-library') _

// Replace the switch statement with config reading
def loadBranchConfig() {
    def configFile = readFile('branch-config.yml')
    def config = readYaml text: configFile
    
    def branchName = env.BRANCH_NAME
    def branchConfig = config.branches[branchName] ?: config.default
    
    // Apply variable substitution
    branchConfig.each { key, value ->
        if (value instanceof String) {
            value = value.replace('{customer_name}', CUSTOMER_NAME.toLowerCase())
            value = value.replace('{branch_name}', branchName)
            value = value.replace('{customer_environment}', CUSTOMER_ENVIRONMENT)
            // Set as environment variable
            env."${key.toUpperCase()}" = value
        }
    }
}

pipeline {
    agent { /* your agent config */ }
    
    stages {
        stage("Load Configuration") {
            steps {
                script {
                    loadBranchConfig()
                }
            }
        }
        
        // Rest of your pipeline stages
    }
}
```

## Why Jinja2 Templating?

### Advantages over Simple String Substitution

**🚀 Powerful Logic**
- Conditional statements: `{% if condition %}...{% else %}...{% endif %}`
- Loops and iterations: `{% for item in list %}...{% endfor %}`
- Built-in filters: `{{ value | upper | replace('old', 'new') }}`
- Function calls: `{{ is_main_branch() }}`, `{{ get_secret_env() }}`

**🧩 Complex Data Structures**
- Nested objects and lists
- Dynamic key generation
- Computed values based on multiple variables

**🔧 Advanced Features**
- Pattern matching for branch names
- Environment-aware configuration
- Macro definitions for reusable templates
- Built-in filters and functions

**📋 Real-world Example**
```yaml
# Simple substitution (old way)
bucket_name: "invent-{customer_name}-input-dev"

# Jinja2 templating (new way)
bucket_name: "invent-{{ customer_name }}-input{% if not is_main_branch() %}-{{ 'dev' if branch_name == 'dev' else branch_name }}{% endif %}"
log_level: "{% if customer_environment.startswith('prod') %}INFO{% else %}DEBUG{% endif %}"
resource_limits:
  cpu: "{% if customer_environment.startswith('prod') %}4{% else %}2{% endif %}"
  memory: "{% if customer_environment.startswith('prod') %}8Gi{% else %}4Gi{% endif %}"
```

## Benefits

1. **🔧 Maintainability**: All branch-specific configuration in one place with powerful templating
2. **📈 Scalability**: Easy to add new branches without modifying pipeline code
3. **🔄 Consistency**: Same configuration logic across different CI/CD systems
4. **🎯 Flexibility**: Support for complex logic, conditionals, and repository-level overrides
5. **📖 Readability**: Clear, declarative configuration format with expressive templating
6. **🧠 Intelligence**: Smart defaults, environment-aware settings, and computed values
7. **🔍 Debugging**: Built-in debug output shows exactly what configuration was applied

## Migration Guide

To migrate from hardcoded branch logic:

1. **Identify Variables**: List all environment variables set in your current switch statements
2. **Create Config**: Create `branch-config.yml` with your branch-specific values
3. **Update Workflow**: Replace hardcoded logic with configuration reading
4. **Test**: Verify all branches work correctly with the new configuration
5. **Clean Up**: Remove old hardcoded switch statements

## Example Repository Structure

```
your-repo/
├── branch-config.yml           # Configuration file
├── .github/
│   └── workflows/
│       └── airflow-deploy.yml  # Updated workflow
├── Jenkinsfile                 # Updated Jenkinsfile (if using Jenkins)
├── dags/                       # Your Airflow DAGs
├── scripts/                    # Your scripts
└── README.md                   # This documentation
```

## 🤔 Why Use Composite Actions?

You asked a great question: "Do we need composite?" The answer is: **it depends on your use case**, but for most scenarios, **composite actions are the best choice**.

### Why Composite Actions Are Recommended:

1. **Clean Interface**: Single line usage in workflows
2. **Dependency Management**: Automatically sets up Python + Jinja2 without users needing to think about it
3. **Modular Architecture**: Clean separation between action definition (`action.yml`) and logic (`process_config.py`)
4. **Reusability**: One action that works across all repositories
5. **Maintainability**: Updates to the logic happen in one place

### Alternative: Direct Python Script

You could skip the composite action and use the Python script directly:

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'

- name: Install dependencies
  run: pip install Jinja2>=3.1.2 PyYAML>=6.0

- name: Process configuration
  run: python3 process_config.py
  env:
    INPUT_BRANCH_NAME: ${{ github.ref_name }}
    INPUT_CUSTOMER_NAME: ${{ vars.CUSTOMER_NAME }}
    # ... all the other environment variables
```

**But this approach requires:**
- 3-4 steps instead of 1
- Users to manage Python dependencies themselves
- More complexity in every workflow that uses it

### Best Practice: Use Composite Actions

The composite action pattern is **GitHub's recommended approach** for exactly this use case - when you need to:
- Set up dependencies
- Run a script
- Export environment variables
- Provide a clean, reusable interface

It's the sweet spot between:
- **JavaScript Actions** (more complex to build, but very fast)
- **Docker Actions** (slower, but completely isolated)
- **Inline shell scripts** (fast but limited and hard to maintain)
