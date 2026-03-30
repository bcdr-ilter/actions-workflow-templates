# CI/CD Pipeline - Input to Output Mapping

## 🎯 **Pipeline Flow with Input-Output Relationships**

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

    %% Configuration flows to all outputs
    I1 --> CONFIG["🌍 Configuration Processing<br/>(Environment Variables)"]
    
    %% Build flows
    I2 --> BUILD["🏗️ Build Process"]
    I4 --> BUILD
    I3 --> BUILD
    I5 --> BUILD

    %% Code flows
    I6 --> CODE["� Code Processing"]
    I7 --> CODE
    I4 --> CODE

    %% Testing flows
    inputs --> TESTS["🧪 Testing & Validation"]

    %% Main processing
    CONFIG --> OUTPUTS["📤 OUTPUTS"]
    BUILD --> OUTPUTS
    CODE --> OUTPUTS
    TESTS --> REPORTS["� Test Reports"]

    %% Styling
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef process fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3,I4,I5,I6,I7 input
    class CONFIG,BUILD,CODE,TESTS process
    class OUTPUTS,REPORTS output
```

## 🔍 **Detailed Input Processing**

```mermaid
graph TD
    subgraph config_flow["� Configuration Flow"]
        C1["� branch-config.yml"] --> C2["🔄 Jinja2 Processing"]
        C2 --> C3["🌍 Environment Variables"]
        
        C3 --> C4["🪣 Storage Paths<br/>(S3/Blob bucket names)"]
        C3 --> C5["☸️ K8s Namespace<br/>({customer} namespaces)"]
        C3 --> C6["🎯 Environment Settings<br/>(prod/dev/uat)"]
    end

    classDef config fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef vars fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class C1,C2 config
    class C3 vars
    class C4,C5,C6 output
```

## 🏗️ **Build & Deployment Flow**

```mermaid
graph TD
    subgraph build_flow["🏗️ Container Build Flow"]
        B1["🐳 .cicd/build/Dockerfile<br/>📋 requirements-build.txt"] --> B2["📦 Base Build Image"]
        B3["🐳 Dockerfile.airflow<br/>📋 requirements-airflow.txt<br/>🎯 dags/"] --> B4["📦 Airflow Image"]
        
        B2 --> B5["🧪 CI Pipeline Container"]
        B4 --> B6["☸️ Kubernetes Deployments"]
    end

    subgraph deploy_flow["🚀 Code Deployment Flow"]
        D1["📜 scripts/<br/>🔧 rocks_extension/<br/>📋 requirements-spark.txt"] --> D2["☁️ Object Storage"]
        D1 --> D3["🏗️ Databricks DBFS"]
        
        D2 --> D4["🪣 AWS S3<br/>s3://{bucket}/src/{env}/"]
        D2 --> D5["🪣 Azure Blob<br/>{account}/{bucket}/src/{env}/"]
        
        D3 --> D6["📁 dbfs:/FileStore/src/{env}/<br/>├── scripts/<br/>├── rocks_extension/<br/>└── requirements"]
    end

    classDef docker fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef image fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef storage fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class B1,B3,D1 docker
    class B2,B4,B5 image
    class B6,D2,D3,D4,D5,D6 storage
```

## 🧪 **Testing & Validation Flow**

```mermaid
graph TD
    subgraph test_flow["🧪 Testing Flow"]
        T1["📜 scripts/<br/>🔧 rocks_extension/<br/>🎯 dags/"] --> T2["🔍 Lint Checks"]
        T1 --> T3["🧪 Unit Tests"]
        T1 --> T4["🔒 Security Scans"]
        
        T2 --> T5["📊 flake8 Report<br/>📊 pylint Report"]
        T3 --> T6["📊 Airflow DAG Tests<br/>📊 Rocks PySpark Tests"]
        T4 --> T7["📊 Gitleaks Results<br/>📊 Trivy Vulnerability Report"]
        
        T8["📄 branch-config.yml"] --> T9["🦄 Pokedex Metadata Check"]
        T9 --> T10["📊 Schema Validation Report"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef process fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef report fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class T1,T8 input
    class T2,T3,T4,T9 process
    class T5,T6,T7,T10 report
```

## 📊 **Input-Output Relationship Matrix**

| Input | Tests Generated | Deployments Generated |
|-------|----------------|----------------------|
| **📄 branch-config.yml** | 🦄 Pokedex Metadata Check | ☁️ All storage paths, ☸️ K8s namespace |
| **🐳 .cicd/build/Dockerfile** | 🔒 Security Scans | 📦 Base Build Image |
| **🐳 Dockerfile.airflow** | 🔒 Security Scans | 📦 Airflow Image, ☸️ K8s deployments |
| **📋 requirements-*.txt** | 🔒 Security Scans | 📦 Both container images |
| **🎯 dags/** | 🔍 Lint, 🎯 Airflow Tests, 🔒 Security | 📦 Airflow Image, ☸️ K8s deployments |
| **📜 scripts/** | 🔍 Lint, 🔒 Security Scans | ☁️ Storage, 🏗️ DBFS |
| **🔧 rocks_extension/** | 🔍 Lint, 🗿 Rocks Tests, 🔒 Security | ☁️ Storage, 🏗️ DBFS |

## 🔗 **Detailed Input-Output Mappings**

### **📄 branch-config.yml → Configuration**
```yaml
Drives all environment variables:
├── Storage bucket names → AWS S3 / Azure Blob paths
├── Kubernetes namespace → K8s deployment target
├── Environment settings → ROCKS_ENV, POKEDEX_ENVIRONMENT
└── Customer settings → All {customer} placeholders
```

### **🐳 .cicd/build/Dockerfile → Base Build Image**
```bash
Input: .cicd/build/Dockerfile + requirements-build.txt
Output: inventkubernetes.azurecr.io/base-images/pipeline-build-image:{hash}
Used by: All subsequent CI/CD jobs for testing and building
```

### **🐳 Dockerfile.airflow → Airflow Runtime**
```bash
Input: Dockerfile.airflow + requirements-airflow.txt + dags/
Output: 
├── Container: inventkubernetes.azurecr.io/airflow/{customer}-{env}:{version}
└── K8s Deployments: airflow-scheduler, airflow-webserver, airflow-worker
```

### **📋 requirements-*.txt → Dependencies**
```bash
requirements-build.txt → Base build image dependencies
requirements-airflow.txt → Airflow runtime dependencies  
requirements-spark.txt → Databricks/Spark execution dependencies
All → Security vulnerability scanning
```

### **🎯 dags/ → Airflow Orchestration**
```bash
Testing:
├── Lint checks (Python syntax/style)
├── DAG import validation
├── Task dependency verification
└── Security scanning

Deployment:
├── Packaged into Airflow container image
└── Deployed to Kubernetes Airflow pods
```

### **📜 scripts/ → Processing Logic**
```bash
Testing:
├── Lint checks (flake8, pylint)
└── Security scanning (secrets, vulnerabilities)

Deployment:
├── AWS S3: s3://{DATASTORE_BUCKET}/src/{ROCKS_ENV}/scripts/
├── Azure Blob: {STORAGE_ACCOUNT}/{DATASTORE_BUCKET}/src/{ROCKS_ENV}/scripts/
└── DBFS: dbfs:/FileStore/src/{ROCKS_ENV}/scripts/
```

### **🔧 rocks_extension/ → Custom Modules**
```bash
Testing:
├── Lint checks (code quality)
├── Unit tests (PySpark functionality)
└── Security scanning

Deployment:
├── AWS S3: s3://{DATASTORE_BUCKET}/src/{ROCKS_ENV}/rocks_extension/
├── Azure Blob: {STORAGE_ACCOUNT}/{DATASTORE_BUCKET}/src/{ROCKS_ENV}/rocks_extension/
└── DBFS: dbfs:/FileStore/src/{ROCKS_ENV}/rocks_extension/
```

## 🎯 **Key Insights**

### **Multi-Output Inputs**
- **📄 branch-config.yml**: Affects ALL deployment paths and configurations
- **🔒 Security Scans**: Applied to ALL code inputs for comprehensive coverage
- **📜 scripts/ & 🔧 rocks_extension/**: Deploy to ALL three storage systems (S3/Blob + DBFS)

### **Specialized Outputs**
- **📦 Container Images**: Built from specific Dockerfiles + requirements
- **☸️ Kubernetes**: Receives Airflow images + configuration from branch-config
- **🧪 Tests**: Each input type has targeted validation (linting, unit tests, security)

### **Configuration Cascade**
The **branch-config.yml** acts as the central configuration source that determines:
- Where everything gets deployed (bucket names, namespaces)
- What environment settings are used (prod/dev/uat)
- How resources are named and organized

This mapping shows how each input file has a specific purpose and creates targeted outputs across both testing and deployment phases! 🚀