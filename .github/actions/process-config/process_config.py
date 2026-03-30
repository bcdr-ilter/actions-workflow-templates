#!/usr/bin/env python3

import os
import yaml
from jinja2 import Environment, BaseLoader


def main():
    # Get inputs from environment with defaults
    branch_name = os.environ.get('INPUT_BRANCH_NAME', 'no-branch-name')
    customer_name = os.environ.get('INPUT_CUSTOMER_NAME', 'default-customer')
    customer_environment = os.environ.get('INPUT_CUSTOMER_ENVIRONMENT', 'dev')
    customer_subdomain = os.environ.get('INPUT_CUSTOMER_SUBDOMAIN', 'dev')
    cloud_provider = os.environ.get('INPUT_CLOUD_PROVIDER', 'azure')
    airflow_version = os.environ.get('INPUT_AIRFLOW_VERSION', '2.4.2')
    airflow_repo_ref = os.environ.get('INPUT_AIRFLOW_REPO_REF', 'latest-nginx-ingress-liveness')
    k8s_cluster = os.environ.get('INPUT_K8S_CLUSTER')

    # Clean up empty string inputs
    branch_name = branch_name.strip() if branch_name else 'no-branch-name'
    if not branch_name:
        branch_name = 'no-branch-name'
    
    customer_name = customer_name.strip() if customer_name else 'default-customer'
    if not customer_name:
        customer_name = 'default-customer'
    customer_name = customer_name.lower()
    
    customer_environment = customer_environment.strip() if customer_environment else 'dev'
    if not customer_environment:
        customer_environment = 'dev'
    
    customer_subdomain = customer_subdomain.strip() if customer_subdomain else 'dev'
    if not customer_subdomain:
        customer_subdomain = 'dev'
    
    cloud_provider = cloud_provider.strip() if cloud_provider else 'azure'
    if not cloud_provider:
        cloud_provider = 'azure'
    
    airflow_version = airflow_version.strip() if airflow_version else '2.4.2'
    if not airflow_version:
        airflow_version = '2.4.2'

    airflow_repo_ref = airflow_repo_ref.strip() if airflow_repo_ref else 'latest-nginx-ingress-liveness'
    if not airflow_repo_ref:
        airflow_repo_ref = 'latest-nginx-ingress-liveness'

    print(f"🔧 Processing configuration for branch: {branch_name}")
    print(f"👤 Customer: {customer_name}")
    print(f"🌍 Environment: {customer_environment}")
    print(f"☁️ Cloud Provider: {cloud_provider}")
    print(f"🚁 Input Airflow Version: {airflow_version}")
    print(f"🚁 Input Airflow Repo Ref: {airflow_repo_ref}")
    print(f"☸️ Input K8S Cluster: {k8s_cluster}")
    print("=" * 50)

    # Load configuration
    try:
        with open('branch-config.yml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ branch-config.yml not found!")
        return
    
    if config is None:
        print("❌ Invalid YAML configuration!")
        return

    # Get branch configuration
    branches = config.get('branches', {})
    if branch_name in branches:
        print(f"📋 Using configuration for branch: {branch_name}")
        branch_config = branches[branch_name]
    else:
        print(f"📋 Branch '{branch_name}' not found in config, using default")
        branch_config = config.get('default', {})

    # Simple Jinja2 templating
    jinja_env = Environment(loader=BaseLoader())
    
    # Template context
    context = {
        'customer_name': customer_name,
        'branch_name': branch_name,
        'customer_environment': customer_environment,
        'customer_subdomain': customer_subdomain,
        'cloud_provider': cloud_provider,
        'airflow_version': airflow_version,
        'airflow_repo_ref': airflow_repo_ref,
        'env': os.environ,  # Allow Jinja2 templates to access environment variables
    }

    # Process configuration values
    processed_config = {}
    for key, value in branch_config.items():
        if isinstance(value, str):
            template = jinja_env.from_string(value)
            processed_config[key] = template.render(context)
        else:
            processed_config[key] = value

    # Add basic required variables (only if not already set by branch config)
    # Check both lowercase and uppercase versions to avoid duplicates
    if 'cloud_provider' not in processed_config and 'CLOUD_PROVIDER' not in processed_config:
        processed_config['cloud_provider'] = cloud_provider
    if 'airflow_version' not in processed_config and 'AIRFLOW_VERSION' not in processed_config:
        processed_config['airflow_version'] = airflow_version
    if 'airflow_repo_ref' not in processed_config and 'AIRFLOW_REPO_REF' not in processed_config:
        processed_config['airflow_repo_ref'] = airflow_repo_ref

    # Add Azure-specific environment variables
    if cloud_provider == 'azure':
        # Set Azure subscription ID based on environment
        if customer_environment == 'prod-us':
            azure_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID_PROD_US')
        elif customer_environment == 'prod-eu':
            azure_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID_PROD_EU')
        else:
            azure_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID_DEV')
        
        if azure_subscription_id:
            processed_config['azure_subscription_id'] = azure_subscription_id
            print(f"📝 Azure Subscription ID: {azure_subscription_id}")
        
        # Set Azure Databricks Client ID
        azure_databricks_client_id = os.environ.get('AZURE_DATABRICKS_CLIENT_ID')
        if azure_databricks_client_id:
            processed_config['azure_databricks_client_id'] = azure_databricks_client_id
            print(f"📝 Azure Databricks Client ID: {azure_databricks_client_id}")
        else:
            processed_config['azure_databricks_client_id'] = 'your-client-id'
            print("⚠️ Azure Databricks Client ID not found, using default")

    # Export environment variables
    print("📤 Exporting environment variables...")
    print(f"🔍 processed_config keys: {list(processed_config.keys())}")
    print(f"🔍 AIRFLOW_REPO_REF value in processed_config: {processed_config.get('airflow_repo_ref', 'NOT FOUND')}")
    github_env = os.environ.get('GITHUB_ENV')
    
    env_vars = {}
    for key, value in processed_config.items():
        env_var_name = key.upper()
        env_var_value = str(value)
        env_vars[env_var_name] = env_var_value
        
        if github_env:
            with open(github_env, 'a') as f:
                f.write(f"{env_var_name}={env_var_value}\n")
            print(f"📝 Wrote to GITHUB_ENV: {env_var_name}={env_var_value}")
        else:
            print(f"⚠️ GITHUB_ENV not available, would write: {env_var_name}={env_var_value}")

    # Add DD_API_KEY, DD_APP_KEY, DD_SITE to GITHUB_ENV if set
    for dd_var in ["DD_API_KEY", "DD_APP_KEY", "DD_SITE"]:
        dd_value = os.environ.get(dd_var)
        if dd_value is not None:
            env_vars[dd_var] = dd_value
            if github_env:
                with open(github_env, 'a') as f:
                    f.write(f"{dd_var}={dd_value}\n")
                print(f"📝 Wrote to GITHUB_ENV: {dd_var}={dd_value}")
            else:
                print(f"⚠️ GITHUB_ENV not available, would write: {dd_var}={dd_value}")

    # Debug output
    print("")
    print("✅ === Configuration Applied ===")
    print(f"🌿 Branch: {branch_name}")
    print(f"👤 Customer: {customer_name}")
    print(f"🪣 Input Bucket: {env_vars.get('INPUT_BUCKET_NAME', 'Not set')}")
    print(f"🪣 Output Bucket: {env_vars.get('OUTPUT_BUCKET_NAME', 'Not set')}")
    print(f"🪣 Datastore Bucket: {env_vars.get('DATASTORE_BUCKET_NAME', 'Not set')}")
    print(f"🔐 Maps Secret: {env_vars.get('MAPS_DATABASE_SECRET_ID', 'Not set')}")
    print(f"🦄 Pokedex Environment: {env_vars.get('POKEDEX_ENVIRONMENT', 'Not set')}")
    print(f"🗿 Rocks Environment: {env_vars.get('ROCKS_ENV', 'Not set')}")
    print(f"🏷️ K8S Namespace: {env_vars.get('K8S_NAMESPACE', 'Not set')}")
    print(f"☸️ K8S Cluster: {env_vars.get('K8S_CLUSTER', 'Not set')}")
    print(f"🌐 Customer Subdomain: {env_vars.get('CUSTOMER_SUBDOMAIN', 'Not set')}")
    print(f"� Airflow Repo Ref: {env_vars.get('AIRFLOW_REPO_REF', 'Not set')}")
    print(f"�📝 Log Level: {env_vars.get('LOG_LEVEL', 'Not set')}")
    if cloud_provider == 'azure':
        print(f"☁️ Azure Subscription ID: {env_vars.get('AZURE_SUBSCRIPTION_ID', 'Not set')}")
        print(f"🔑 Azure Databricks Client ID: {env_vars.get('AZURE_DATABRICKS_CLIENT_ID', 'Not set')}")
    print("========================================")


if __name__ == '__main__':
    main() 
