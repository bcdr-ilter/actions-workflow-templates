# 🚀 Usage Examples

This document shows practical examples of how to use the configuration-driven CI/CD pipelines in different scenarios.

## 📋 Step-by-Step Setup

### 1. Copy Pipeline File
Choose one of the pipeline files and copy it to your repository:

```bash
# For simple deployments
cp .github/workflows/simple-deploy.yml your-repo/.github/workflows/

# For complex deployments
cp .github/workflows/deploy-application.yml your-repo/.github/workflows/
```

### 2. Set Repository Variables
In your GitHub repository, go to **Settings → Secrets and Variables → Actions → Variables** and add:

```
CUSTOMER_NAME=WBA
CUSTOMER_ENVIRONMENT=prod-eu
CUSTOMER_SUBDOMAIN=prod
CLOUD_PROVIDER=azure
AIRFLOW_VERSION=2.4.2
```

### 3. Set Repository Secrets
In **Settings → Secrets and Variables → Actions → Secrets**, add your credentials:

```
# Core cloud credentials
AZURE_CREDENTIALS={"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"..."}
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Application secrets
FERNET_KEY=your-fernet-key
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# Database credentials
POSTGRES_CREDENTIALS_USR=username
POSTGRES_CREDENTIALS_PSW=password

# Azure-specific (if using Azure)
AZURE_DATABRICKS_CLIENT_ID=your-databricks-client-id
STORAGE_ACCOUNT_ACCESS_KEY=your-storage-key

# Repository access (if needed)
GH_PAT=ghp_your-github-token
```

### 3.1. Set Azure Multi-Environment Variables (If Using Azure)
For Azure multi-environment support, also add these variables:

```
AZURE_SUBSCRIPTION_ID_PROD_US=subscription-id-for-us-prod
AZURE_SUBSCRIPTION_ID_PROD_EU=subscription-id-for-eu-prod
AZURE_SUBSCRIPTION_ID_DEV=subscription-id-for-dev
AZURE_TENANT_ID=your-tenant-id
STORAGE_ACCOUNT_NAME=your-storage-account
```

### 4. Create branch-config.yml (Optional)
If you want custom configuration, create `branch-config.yml` in your repository root:

```yaml
branches:
  main:
    input_bucket_name: "mycompany-{{ customer_name }}-input"
    output_bucket_name: "mycompany-{{ customer_name }}-output"
    k8s_namespace: "{{ customer_name }}-prod"
    
  dev:
    input_bucket_name: "mycompany-{{ customer_name }}-input-dev"
    output_bucket_name: "mycompany-{{ customer_name }}-output-dev"
    k8s_namespace: "{{ customer_name }}-dev"

# 🔐 Configure secrets and cloud variables through configuration
global:
  azure:
    subscription_id: "{% if customer_environment == 'prod-us' %}{{ env.AZURE_SUBSCRIPTION_ID_PROD_US }}{% elif customer_environment == 'prod-eu' %}{{ env.AZURE_SUBSCRIPTION_ID_PROD_EU }}{% else %}{{ env.AZURE_SUBSCRIPTION_ID_DEV }}{% endif %}"
    databricks_client_id: "{{ env.AZURE_DATABRICKS_CLIENT_ID }}"
    
  secrets:
    fernet_key: "{{ env.FERNET_KEY }}"
    sentry_dsn: "{{ env.SENTRY_DSN }}"
```

## 🎯 Real-World Examples

### Example 1: Simple Microservice Deployment

```yaml
name: Deploy Microservice

on:
  push:
    branches: [ main, dev ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Process Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.ref_name }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
          cloud-provider: ${{ vars.CLOUD_PROVIDER }}
          
      - name: Build and Deploy
        run: |
          # Build Docker image
          docker build -t my-app:${{ github.sha }} .
          
          # Deploy to Kubernetes
          kubectl apply -f k8s/deployment.yaml -n $K8S_NAMESPACE
          kubectl set image deployment/my-app app=my-app:${{ github.sha }} -n $K8S_NAMESPACE
```

### Example 2: Data Pipeline with Storage

```yaml
name: Data Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  process-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Process Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.ref_name }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
          cloud-provider: ${{ vars.CLOUD_PROVIDER }}
          
      - name: Run Data Processing
        run: |
          # Download data from input bucket
          aws s3 sync s3://$INPUT_BUCKET_NAME/raw-data ./data/
          
          # Process data
          python process_data.py --env $POKEDEX_ENVIRONMENT --log-level $LOG_LEVEL
          
          # Upload results to output bucket
          aws s3 sync ./results s3://$OUTPUT_BUCKET_NAME/processed/
```

### Example 3: Multi-Environment with Overrides

```yaml
name: Multi-Environment Deploy

on:
  push:
    branches: [ main, dev, staging ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Process Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.ref_name }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
          cloud-provider: ${{ vars.CLOUD_PROVIDER }}
          # Override buckets for this specific repository
          input-bucket-name: ${{ vars.SPECIAL_INPUT_BUCKET }}
          output-bucket-name: ${{ vars.SPECIAL_OUTPUT_BUCKET }}
          
      - name: Deploy Application
        run: |
          echo "Deploying to $K8S_NAMESPACE with special buckets"
          echo "Input: $INPUT_BUCKET_NAME"
          echo "Output: $OUTPUT_BUCKET_NAME"
          
          # Your deployment logic here
```

### Example 4: Feature Branch Testing

```yaml
name: Feature Branch Test

on:
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Process Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.head_ref }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: 'dev'  # Force dev environment for testing
          cloud-provider: ${{ vars.CLOUD_PROVIDER }}
          
      - name: Deploy Test Environment
        run: |
          echo "Creating test environment: $K8S_NAMESPACE"
          
          # Create temporary namespace
          kubectl create namespace $K8S_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
          
          # Deploy test version
          kubectl apply -f k8s/test-deployment.yaml -n $K8S_NAMESPACE
          
      - name: Run Integration Tests
        run: |
          echo "Running tests against $K8S_NAMESPACE"
          pytest tests/integration/ --namespace=$K8S_NAMESPACE
```

### Example 5: Azure Multi-Environment with Secrets

```yaml
name: Azure Multi-Environment Deploy

on:
  push:
    branches: [ main, dev ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    env:
      # Secrets are automatically available
      AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
      FERNET_KEY: ${{ secrets.FERNET_KEY }}
      AZURE_DATABRICKS_CLIENT_ID: ${{ secrets.AZURE_DATABRICKS_CLIENT_ID }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Process Configuration
        uses: inventanalytics/actions-workflow-templates/.github/actions/process-config@main
        with:
          branch-name: ${{ github.ref_name }}
          customer-name: ${{ vars.CUSTOMER_NAME }}
          customer-environment: ${{ vars.CUSTOMER_ENVIRONMENT }}
          cloud-provider: 'azure'
          
      - name: Set Environment-Specific Variables
        run: |
          # This automatically sets the correct Azure subscription based on environment
          case "${{ vars.CUSTOMER_ENVIRONMENT }}" in
            prod-us)
              echo "AZURE_SUBSCRIPTION_ID=${{ vars.AZURE_SUBSCRIPTION_ID_PROD_US }}" >> $GITHUB_ENV
              ;;
            prod-eu)
              echo "AZURE_SUBSCRIPTION_ID=${{ vars.AZURE_SUBSCRIPTION_ID_PROD_EU }}" >> $GITHUB_ENV
              ;;
            *)
              echo "AZURE_SUBSCRIPTION_ID=${{ vars.AZURE_SUBSCRIPTION_ID_DEV }}" >> $GITHUB_ENV
              ;;
          esac
          
          # Set Azure Databricks client ID with fallback
          if [[ -n "${{ secrets.AZURE_DATABRICKS_CLIENT_ID }}" ]]; then
            echo "AZURE_DATABRICKS_CLIENT_ID=${{ secrets.AZURE_DATABRICKS_CLIENT_ID }}" >> $GITHUB_ENV
            echo "✅ Azure Databricks configured"
          else
            echo "⚠️ Azure Databricks client ID not found"
          fi
          
      - name: Deploy to Azure
        run: |
          echo "Deploying to Azure subscription: $AZURE_SUBSCRIPTION_ID"
          echo "Using storage account: ${{ vars.STORAGE_ACCOUNT_NAME }}"
          echo "Deploying to namespace: $K8S_NAMESPACE"
          
          # Login to Azure
          az login --service-principal --username $clientId --password $clientSecret --tenant $tenantId
          
          # Deploy to AKS
          az aks get-credentials --resource-group $K8S_CLUSTER_RG --name $K8S_CLUSTER
          kubectl apply -f manifests/ -n $K8S_NAMESPACE
```

## 🔧 Common Patterns

### Pattern 1: Conditional Deployment
```yaml
- name: Deploy to Production
  if: github.ref == 'refs/heads/main' && env.POKEDEX_ENVIRONMENT == 'wba'
  run: |
    echo "Deploying to production: $K8S_NAMESPACE"
    # Production deployment logic
```

### Pattern 2: Multi-Cloud Deployment
```yaml
- name: Deploy to Cloud
  run: |
    if [ "$CLOUD_PROVIDER" = "azure" ]; then
      az aks get-credentials --name $K8S_CLUSTER --resource-group $K8S_CLUSTER_RG
    elif [ "$CLOUD_PROVIDER" = "aws" ]; then
      aws eks update-kubeconfig --name $K8S_CLUSTER
    fi
    
    kubectl apply -f manifests/ -n $K8S_NAMESPACE
```

### Pattern 3: Configuration Validation
```yaml
- name: Validate Configuration
  run: |
    echo "Validating configuration..."
    echo "Environment: $POKEDEX_ENVIRONMENT"
    echo "Namespace: $K8S_NAMESPACE"
    echo "Buckets: $INPUT_BUCKET_NAME, $OUTPUT_BUCKET_NAME"
    
    # Add validation logic
    if [ -z "$INPUT_BUCKET_NAME" ]; then
      echo "❌ INPUT_BUCKET_NAME is not set"
      exit 1
    fi
    
    echo "✅ Configuration is valid"
```

## 🆘 Troubleshooting

### Common Issues

1. **Environment variables not available**
   - Make sure to run the composite action first
   - Check that repository variables are set correctly

2. **Wrong bucket names**
   - Verify your `branch-config.yml` templates
   - Check the Jinja2 syntax in your templates

3. **Kubernetes deployment fails**
   - Ensure `K8S_CLUSTER` and `K8S_CLUSTER_RG` are correct
   - Verify cloud credentials are properly configured

### Debug Mode

Add this step to debug configuration issues:

```yaml
- name: Debug Configuration
  run: |
    echo "=== Debug Information ==="
    echo "Branch: ${{ github.ref_name }}"
    echo "Customer: ${{ vars.CUSTOMER_NAME }}"
    echo "Environment: ${{ vars.CUSTOMER_ENVIRONMENT }}"
    echo "All environment variables:"
    env | grep -E "(INPUT_|OUTPUT_|K8S_|POKEDEX_|ROCKS_|MAPS_)" | sort
```

## 💡 Best Practices

1. **Use descriptive branch names** - They become part of your namespace
2. **Configure secrets in branch-config.yml** - Use `{{ env.SECRET_NAME }}` instead of hardcoding in workflows
3. **Set up monitoring** - Use the exported variables in your monitoring setup
4. **Test in dev first** - Always test configuration changes in dev branches
5. **Document your overrides** - If you use repository variable overrides, document why
6. **Use secrets properly** - Never put sensitive data in repository variables

## 🔐 Configuration-Driven Secret Management

### ✅ **Recommended Approach** - Configuration-Driven

Instead of hardcoding secrets in workflows:
```yaml
# ❌ Don't do this in workflows
env:
  AZURE_DATABRICKS_CLIENT_ID: ${{ secrets.AZURE_DATABRICKS_CLIENT_ID }}
```

Configure them in `branch-config.yml`:
```yaml
# ✅ Do this in branch-config.yml
global:
  azure:
    databricks_client_id: "{{ env.AZURE_DATABRICKS_CLIENT_ID }}"
    subscription_id: "{% if customer_environment == 'prod' %}{{ env.AZURE_SUBSCRIPTION_ID_PROD }}{% else %}{{ env.AZURE_SUBSCRIPTION_ID_DEV }}{% endif %}"
```

### Benefits:
- ✅ **Environment-aware**: Different values per environment using Jinja2
- ✅ **Centralized**: All configuration in one place
- ✅ **Flexible**: Can use conditionals, filters, and computed values
- ✅ **Maintainable**: Changes don't require workflow updates
- ✅ **Consistent**: Same approach across all repositories

## 🎓 Next Steps

- Read the [main README](README.md) for detailed configuration options
- Check out the [branch-config.yml examples](branch-config.yml)
- Set up your repository variables and secrets
- Start with the simple pipeline and add complexity as needed 
