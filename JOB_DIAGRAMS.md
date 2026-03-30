# CI/CD Jobs - Individual Input/Output Diagrams

## 🏗️ **Job 1: `build_base_image`**

```mermaid
graph TD
    subgraph inputs1["📥 INPUTS"]
        I1["🐳 .cicd/build/Dockerfile"]
        I2["📋 requirements-*.txt<br/>(build, spark, airflow)"]
        I3["🔐 Azure/AWS Credentials"]
    end

    inputs1 --> JOB1["🏗️ build_base_image<br/>Hash → Build → Push"]

    JOB1 --> outputs1["📤 OUTPUTS"]

    subgraph outputs1["📤 OUTPUTS"]
        O1["📦 Base Build Image<br/>inventkubernetes.azurecr.io/<br/>base-images/pipeline-build-image:{hash}"]
        O2["🏷️ image_tag<br/>(for downstream jobs)"]
        O3["✅ Image Exists Check<br/>(skip if already built)"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3 input
    class JOB1 job
    class O1,O2,O3 output
```

---

## 🧪 **Job 2: `ci-pipeline`**

```mermaid
graph TD
    subgraph inputs2["📥 INPUTS"]
        I1["🖼️ Base Image<br/>(from build_base_image)"]
        I2["📄 branch-config.yml"]
        I3["🎯 dags/"]
        I4["📜 scripts/"]
        I5["🔧 rocks_extension/"]
        I6["🔧 Customer Variables<br/>(CUSTOMER_NAME, etc.)"]
    end

    inputs2 --> JOB2["🧪 ci-pipeline<br/>Test → Lint → Validate"]

    JOB2 --> outputs2["📤 OUTPUTS"]

    subgraph outputs2["📤 OUTPUTS"]
        O1["🌍 Environment Variables<br/>(INPUT_BUCKET_NAME, K8S_NAMESPACE, etc.)"]
        O2["📊 Lint Results<br/>(flake8, pylint reports)"]
        O3["✅ Airflow Unit Tests<br/>(DAG validation results)"]
        O4["✅ Rocks Unit Tests<br/>(PySpark test results)"]
        O5["🦄 Pokedex Metadata Check<br/>(Schema validation)"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3,I4,I5,I6 input
    class JOB2 job
    class O1,O2,O3,O4,O5 output
```

---

## 🚀 **Job 3: `deploy-scripts`**

```mermaid
graph TD
    subgraph inputs3["📥 INPUTS"]
        I1["📜 scripts/"]
        I2["🔧 rocks_extension/"]
        I3["📋 requirements-spark.txt"]
        I4["🌍 Environment Variables<br/>(from ci-pipeline)"]
        I5["🔐 Cloud Credentials<br/>(AWS/Azure/Databricks)"]
    end

    inputs3 --> JOB3["🚀 deploy-scripts<br/>Generate → Upload → Sync"]

    JOB3 --> outputs3["📤 OUTPUTS"]

    subgraph outputs3["📤 OUTPUTS"]
        O1["☁️ AWS S3<br/>s3://{DATASTORE_BUCKET}/src/{ROCKS_ENV}/<br/>├── scripts/<br/>├── rocks_extension/<br/>└── requirements_spark.txt"]
        O2["☁️ Azure Blob<br/>{STORAGE_ACCOUNT}/{DATASTORE_BUCKET}/<br/>src/{ROCKS_ENV}/<br/>├── scripts/<br/>└── rocks_extension/"]
        O3["🏗️ Databricks DBFS<br/>dbfs:/FileStore/src/{ROCKS_ENV}/<br/>├── scripts/<br/>├── rocks_extension/<br/>├── module_runner.py<br/>├── internal_packages.lock<br/>└── requirements_spark.txt"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3,I4,I5 input
    class JOB3 job
    class O1,O2,O3 output
```

---

## 📦 **Job 4: `build-airflow-image`**

```mermaid
graph TD
    subgraph inputs4["📥 INPUTS"]
        I1["🐳 Dockerfile.airflow"]
        I2["📋 requirements-airflow.txt"]
        I3["🎯 dags/"]
        I4["🔐 Registry Credentials<br/>(Azure ACR / AWS ECR)"]
        I5["🌿 Branch Name<br/>(for image tagging)"]
    end

    inputs4 --> JOB4["📦 build-airflow-image<br/>Hash → Build → Tag → Push"]

    JOB4 --> outputs4["📤 OUTPUTS"]

    subgraph outputs4["📤 OUTPUTS"]
        O1["📦 Azure Airflow Image<br/>inventkubernetes.azurecr.io/<br/>airflow/{customer}-{env}:{version}"]
        O2["📦 AWS Airflow Image<br/>{account}.dkr.ecr.eu-west-1.amazonaws.com/<br/>airflow/{customer}-{env}:{version}"]
        O3["🏷️ airflow_image_version<br/>(for deploy-airflow job)"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3,I4,I5 input
    class JOB4 job
    class O1,O2,O3 output
```

---

## ☸️ **Job 5: `deploy-airflow`**

```mermaid
graph TD
    subgraph inputs5["📥 INPUTS"]
        I1["🏷️ airflow_image_version<br/>(from build-airflow-image)"]
        I2["📁 K8s Manifests<br/>(from external k8s repo)"]
        I3["🌍 Environment Variables<br/>(from ci-pipeline)"]
        I4["🔐 Kubernetes Credentials<br/>(kubeconfig/service account)"]
        I5["📄 .env.tpl<br/>(environment template)"]
    end

    inputs5 --> JOB5["☸️ deploy-airflow<br/>Template → Apply → Deploy"]

    JOB5 --> outputs5["📤 OUTPUTS"]

    subgraph outputs5["📤 OUTPUTS"]
        O1["☸️ Airflow Scheduler<br/>Deployment in {K8S_NAMESPACE}"]
        O2["☸️ Airflow Webserver<br/>Deployment + Service in {K8S_NAMESPACE}"]
        O3["☸️ Airflow Worker<br/>Deployment in {K8S_NAMESPACE}<br/>(if CeleryExecutor)"]
        O4["📋 ConfigMaps<br/>(airflow.cfg, environment variables)"]
        O5["🔐 Secrets<br/>(database, fernet key, cloud credentials)"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3,I4,I5 input
    class JOB5 job
    class O1,O2,O3,O4,O5 output
```

---

## 🔒 **Bonus Job: `code-scan` (Parallel)**

```mermaid
graph TD
    subgraph inputs6["📥 INPUTS"]
        I1["📁 Full Repository<br/>(all files and git history)"]
        I2["🔐 GitHub Token<br/>(for uploading results)"]
        I3["🔐 Gitleaks License<br/>(if using pro features)"]
    end

    inputs6 --> JOB6["🔒 code-scan<br/>Scan → Analyze → Report"]

    JOB6 --> outputs6["📤 OUTPUTS"]

    subgraph outputs6["📤 OUTPUTS"]
        O1["🔍 Gitleaks Results<br/>(Secret detection report)"]
        O2["🛡️ Trivy Scan Results<br/>(Vulnerability assessment)"]
        O3["📊 SARIF Reports<br/>(GitHub Security tab)"]
        O4["📋 Security Summary<br/>(Table format output)"]
    end

    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#000
    classDef output fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class I1,I2,I3 input
    class JOB6 job
    class O1,O2,O3,O4 output
```

## 📊 **Job Dependencies Summary**

```mermaid
graph LR
    J1["🏗️ build_base_image"] --> J2["🧪 ci-pipeline"]
    J2 --> J3["🚀 deploy-scripts"]
    J2 --> J4["📦 build-airflow-image"]
    J3 --> J5["☸️ deploy-airflow"]
    J4 --> J5
    J2 -.-> J6["🔒 code-scan<br/>(parallel)"]

    classDef job fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    class J1,J2,J3,J4,J5,J6 job
```

## 🎯 **Key Job Characteristics**

| Job | Type | Duration | Dependencies | Parallel? |
|-----|------|----------|--------------|-----------|
| **🏗️ build_base_image** | Build | ~5-10 min | None | ❌ |
| **🧪 ci-pipeline** | Test | ~10-15 min | build_base_image | ❌ |
| **🚀 deploy-scripts** | Deploy | ~3-5 min | ci-pipeline ✅ | ❌ |
| **📦 build-airflow-image** | Build | ~5-8 min | ci-pipeline ✅ | ✅ (with deploy-scripts) |
| **☸️ deploy-airflow** | Deploy | ~2-3 min | deploy-scripts + build-airflow-image | ❌ |
| **🔒 code-scan** | Security | ~2-5 min | None | ✅ (fully parallel) |

## 💡 **Optimization Notes**

- **🏗️ Base image**: Uses hash-based caching - skips rebuild if image exists
- **📦 Airflow image**: Version-based tagging prevents unnecessary rebuilds  
- **🚀 Scripts deployment**: Runs in parallel with Airflow image build for efficiency
- **🔒 Security scanning**: Runs completely parallel to save time
- **☸️ K8s deployment**: Only runs after all dependencies complete successfully

Each job has a **clear purpose** and **well-defined inputs/outputs**, making the pipeline **modular** and **maintainable**! 🚀