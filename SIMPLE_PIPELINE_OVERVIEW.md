# CI/CD Pipeline - Simple Input/Output View

## 🎯 **Pipeline Flow Overview**

```mermaid
graph TD
    subgraph inputs["📥 PIPELINE INPUTS"]
        I1["📄 branch-config.yml<br/>(Branch-specific settings)"]
        I2["🐳 .cicd/build/Dockerfile<br/>(Base build environment)"]
        I3["🐳 Dockerfile.airflow<br/>(Airflow runtime)"]
        I4["📋 requirements-*.txt<br/>(Python dependencies)"]
        I5["🎯 dags/<br/>(Airflow DAGs)"]
        I6["📜 scripts/<br/>(Processing scripts)"]
        I7["🔧 rocks_extension/<br/>(Custom modules)"]
    end

    inputs --> CICD["🔄 CI/CD PIPELINE<br/>GitHub Actions"]

    CICD --> tests["🧪 TESTS & VALIDATION"]
    CICD --> deployments["🚀 DEPLOYMENTS"]

    subgraph tests["🧪 Tests & Validation"]
        T1["🔍 Lint Results<br/>(flake8, pylint)"]
        T2["� Airflow Unit Tests<br/>(DAG validation)"]
        T3["🗿 Rocks Unit Tests<br/>(PySpark modules)"]
        T4["🦄 Pokedex Metadata Check<br/>(Schema validation)"]
        T5["🔒 Security Scans<br/>(Gitleaks + Trivy)"]
    end

    subgraph deployments["🚀 Deployments"]
        subgraph images["🐳 Container Images"]
            O1["📦 Base Build Image<br/>inventkubernetes.azurecr.io/<br/>base-images/pipeline-build-image"]
            O2["📦 Airflow Image<br/>inventkubernetes.azurecr.io/<br/>airflow/{customer}-{env}"]
        end

        subgraph storage["☁️ Object Storage"]
            O3["🪣 AWS S3<br/>s3://{DATASTORE_BUCKET}/<br/>src/{ROCKS_ENV}/"]
            O4["🪣 Azure Blob<br/>{STORAGE_ACCOUNT}/<br/>{DATASTORE_BUCKET}/"]
        end

        subgraph dbfs["🏗️ Databricks DBFS"]
            O5["📁 dbfs:/FileStore/<br/>src/{ROCKS_ENV}/<br/>├── scripts/<br/>├── rocks_extension/<br/>└── requirements"]
        end

        subgraph k8s["☸️ Kubernetes"]
            O6["🎯 Namespace: {K8S_NAMESPACE}<br/>├── airflow-scheduler<br/>├── airflow-webserver<br/>└── airflow-worker"]
        end
    end

    %% Styling
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef pipeline fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef tests fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3,I4,I5,I6,I7 input
    class CICD pipeline
    class T1,T2,T3,T4,T5 tests
    class O1,O2,O3,O4,O5,O6 output
```

## 📂 **Test & Validation Outputs**

### **🧪 Test Results**
```bash
🔍 Lint Results:
   - flake8 output (code style violations)
   - pylint reports (code quality metrics)
   - Exit codes: 0 (pass) or >0 (issues found)

🎯 Airflow Unit Tests:
   - DAG syntax validation
   - Import tests for all DAGs
   - Task dependency verification
   - Custom operator testing

🗿 Rocks Unit Tests:
   - PySpark module testing
   - Data transformation validation
   - Custom function unit tests
   - Integration test results

🦄 Pokedex Metadata Check:
   - Schema validation against metadata repository
   - Table structure verification
   - Column type consistency checks
   - Data lineage validation

🔒 Security Scan Results:
   - Gitleaks: Secret detection in code/history
   - Trivy: Vulnerability scanning (dependencies & containers)
   - SARIF reports uploaded to GitHub Security tab
```

## 📂 **Deployment Outputs**

### **🐳 Container Images**
```bash
# Base Build Image (cached, reused across builds)
inventkubernetes.azurecr.io/base-images/pipeline-build-image:{hash}

# Airflow Images (per customer/environment)
Azure: inventkubernetes.azurecr.io/airflow/{customer}-{env}:{version}
AWS:   {account}.dkr.ecr.eu-west-1.amazonaws.com/airflow/{customer}-{env}:{version}
```

### **☁️ Object Storage Paths**
```bash
# AWS S3 Structure
s3://{DATASTORE_BUCKET_NAME}/src/{ROCKS_ENV}/
├── scripts/                    # Processing scripts
├── rocks_extension/            # Custom Python modules  
├── internal-packages.lock      # Dependency lock file
└── requirements_spark.txt      # Spark requirements

# Azure Blob Structure  
{STORAGE_ACCOUNT}/{DATASTORE_BUCKET}/src/{ROCKS_ENV}/
├── scripts/
└── rocks_extension/
```

### **🏗️ Databricks DBFS**
```bash
dbfs:/FileStore/src/{ROCKS_ENV}/
├── scripts/                    # Same as object storage
├── rocks_extension/            # Same as object storage
├── module_runner.py            # Execution wrapper
├── internal_packages.lock      # Dependency management
└── requirements_spark.txt      # Spark dependencies
```

### **☸️ Kubernetes Deployments**
```yaml
Namespace: {K8S_NAMESPACE}      # Typically: customer name

Deployments:
  - airflow-scheduler           # DAG scheduling
  - airflow-webserver          # Web UI + API
  - airflow-worker             # Task execution (if Celery)

ConfigMaps:
  - airflow-config             # airflow.cfg
  - environment-variables      # From branch-config.yml

Secrets:
  - database-connection        # Airflow metadata DB
  - fernet-key                # Encryption key
  - cloud-credentials         # AWS/Azure access
```

## 🌍 **Configuration Variables**

Generated from `branch-config.yml` using **Jinja2 templating**:

| Variable | Example Value | Purpose |
|----------|---------------|---------|
| `INPUT_BUCKET_NAME` | `invent-{customer}-input` | Data input bucket |
| `OUTPUT_BUCKET_NAME` | `invent-{customer}-output` | Results bucket |
| `DATASTORE_BUCKET_NAME` | `invent-{customer}-wba-datastore` | Scripts/code storage |
| `K8S_NAMESPACE` | `{customer_name}` | Kubernetes isolation |
| `POKEDEX_ENVIRONMENT` | `wba` / `dev` | Metadata environment |
| `ROCKS_ENV` | `prod` / `dev` | Processing environment |
| `MAPS_DATABASE_SECRET_ID` | `{customer}-{env}-app` | Database credentials |

## 🔄 **Branch-Based Behavior**

| Branch | Environment | Image Tag | Storage Path | K8s Namespace |
|--------|-------------|-----------|--------------|---------------|
| `main` | Production | `prod` | `/prod/` | `{customer}` |
| `dev` | Development | `dev` | `/dev/` | `{customer}-dev` |
| `feature/*` | Feature | `dev` | `/dev/` | `{customer}-dev` |
| `uat` | UAT | `uat` | `/uat/` | `{customer}-uat` |

The pipeline automatically deploys to different environments based on the Git branch, with all paths and configurations dynamically generated from the `branch-config.yml` template.