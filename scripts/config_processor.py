#!/usr/bin/env python3
"""
Configuration processor for CI/CD pipelines using Jinja2 templating.
This script reads the branch-config.yml file and applies Jinja2 templating
to generate environment-specific configuration values.
"""

import os
import sys
import yaml
import argparse
from jinja2 import Environment, BaseLoader, select_autoescape
from typing import Dict, Any


class ConfigProcessor:
    def __init__(self, config_file: str = 'branch-config.yml'):
        self.config_file = config_file
        self.jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def load_config(self) -> Dict[str, Any]:
        """Load the YAML configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {self.config_file} not found", file=sys.stderr)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_branch_config(self, config: Dict[str, Any], branch_name: str) -> Dict[str, Any]:
        """Get configuration for a specific branch, falling back to default if not found."""
        branches = config.get('branches', {})
        if branch_name in branches:
            print(f"Using configuration for branch: {branch_name}")
            return branches[branch_name]
        else:
            print(f"Branch '{branch_name}' not found in config, using default")
            return config.get('default', {})
    
    def create_template_context(self, **kwargs) -> Dict[str, Any]:
        """Create the template context with all available variables."""
        context = {
            'customer_name': kwargs.get('customer_name', '').lower(),
            'branch_name': kwargs.get('branch_name', ''),
            'customer_environment': kwargs.get('customer_environment', ''),
            'customer_subdomain': kwargs.get('customer_subdomain', ''),
            'cloud_provider': kwargs.get('cloud_provider', ''),
            'airflow_version': kwargs.get('airflow_version', ''),
            
            # Helper functions
            'env': os.environ,
            'is_main_branch': lambda: kwargs.get('branch_name') == 'main',
            'is_dev_branch': lambda: kwargs.get('branch_name') == 'dev',
            'is_feature_branch': lambda: kwargs.get('branch_name', '').startswith('feature'),
            'get_secret_env': lambda: 'prod' if kwargs.get('branch_name') == 'main' else 'dev',
        }
        
        # Add any additional context variables
        for key, value in kwargs.items():
            if key not in context:
                context[key] = value
                
        return context
    
    def render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 template string with the given context."""
        try:
            template = self.jinja_env.from_string(str(template_str))
            return template.render(context)
        except Exception as e:
            print(f"Error rendering template '{template_str}': {e}", file=sys.stderr)
            return str(template_str)  # Return original string if rendering fails
    
    def process_config_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Process a configuration value, applying Jinja2 templating if it's a string."""
        if isinstance(value, str):
            return self.render_template(value, context)
        elif isinstance(value, dict):
            return {k: self.process_config_value(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process_config_value(item, context) for item in value]
        else:
            return value
    
    def process_branch_config(self, branch_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process all values in a branch configuration using Jinja2 templating."""
        processed_config = {}
        
        for key, value in branch_config.items():
            processed_value = self.process_config_value(value, context)
            processed_config[key] = processed_value
            
        return processed_config
    
    def get_maps_database_secret_id(self, customer_name: str, branch_name: str, 
                                   cloud_provider: str) -> str:
        """Generate the maps database secret ID based on cloud provider and branch."""
        secret_env = 'prod' if branch_name == 'main' else 'dev'
        customer_lower = customer_name.lower()
        
        if cloud_provider == 'azure':
            return f"{customer_lower}-{secret_env}-app"
        else:
            return f"{customer_lower}/{secret_env}/app"
    
    def get_k8s_cluster_info(self, branch_name: str, customer_environment: str, 
                            cloud_provider: str, k8s_cluster_var: Optional[str] = None) -> Dict[str, str]:
        """Get Kubernetes cluster information based on branch and environment."""
        if cloud_provider == 'aws':
            k8s_cluster = k8s_cluster_var or 'default-cluster'
            k8s_cluster_rg = f"{customer_environment}-rg"
        else:
            if branch_name == 'main':
                k8s_cluster = k8s_cluster_var or customer_environment
                k8s_cluster_rg = f"{customer_environment}-rg"
            else:
                if customer_environment == 'dev':
                    k8s_cluster = 'dev'
                    k8s_cluster_rg = 'dev-rg'
                else:
                    k8s_cluster = 'customertest-eu'
                    k8s_cluster_rg = 'prod-eu-rg'
        
        return {
            'k8s_cluster': k8s_cluster,
            'k8s_cluster_rg': k8s_cluster_rg
        }
    
    def process_configuration(self, **kwargs) -> Dict[str, str]:
        """Main method to process configuration and return environment variables."""
        # Load configuration
        config = self.load_config()
        
        # Get branch-specific configuration
        branch_name = kwargs.get('branch_name', '')
        branch_config = self.get_branch_config(config, branch_name)
        
        # Create template context
        context = self.create_template_context(**kwargs)
        
        # Process configuration with Jinja2
        processed_config = self.process_branch_config(branch_config, context)
        
        # Generate additional computed values
        customer_name = kwargs.get('customer_name', '')
        cloud_provider = kwargs.get('cloud_provider', '')
        customer_environment = kwargs.get('customer_environment', '')
        
        # Maps database secret ID
        processed_config['maps_database_secret_id'] = self.get_maps_database_secret_id(
            customer_name, branch_name, cloud_provider
        )
        
        # K8s cluster information
        k8s_cluster_var = kwargs.get('k8s_cluster')
        k8s_info = self.get_k8s_cluster_info(branch_name, customer_environment, cloud_provider, k8s_cluster_var)
        processed_config.update(k8s_info)
        
        # Convert all values to strings for environment variables
        env_vars = {}
        for key, value in processed_config.items():
            env_var_name = key.upper()
            env_vars[env_var_name] = str(value)
        
        return env_vars
    
    def export_to_github_env(self, env_vars: Dict[str, str], output_file: Optional[str] = None):
        """Export environment variables to GitHub Actions environment."""
        github_env = output_file or os.environ.get('GITHUB_ENV')
        
        if github_env:
            with open(github_env, 'a') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
        else:
            # Print to stdout if no GITHUB_ENV file
            for key, value in env_vars.items():
                print(f"{key}={value}")
    
    def print_debug_info(self, env_vars: Dict[str, str], branch_name: str, customer_name: str):
        """Print debug information about the applied configuration."""
        print("\n=== Configuration Applied ===")
        print(f"Branch: {branch_name}")
        print(f"Customer: {customer_name}")
        
        # Print key variables
        key_vars = [
            'INPUT_BUCKET_NAME', 'OUTPUT_BUCKET_NAME', 'DATASTORE_BUCKET_NAME',
            'MAPS_DATABASE_SECRET_ID', 'POKEDEX_ENVIRONMENT', 'ROCKS_ENV',
            'K8S_NAMESPACE', 'IMAGE_ENV', 'K8S_CLUSTER', 'K8S_CLUSTER_RG',
            'CUSTOMER_SUBDOMAIN'
        ]
        
        for var in key_vars:
            value = env_vars.get(var, 'Not set')
            print(f"{var}: {value}")


def main():
    parser = argparse.ArgumentParser(description='Process CI/CD configuration with Jinja2 templating')
    parser.add_argument('--config-file', default='branch-config.yml', 
                       help='Path to configuration file (default: branch-config.yml)')
    parser.add_argument('--branch-name', required=True, 
                       help='Branch name to process configuration for')
    parser.add_argument('--customer-name', required=True, 
                       help='Customer name')
    parser.add_argument('--customer-environment', required=True, 
                       help='Customer environment (e.g., prod-eu, dev)')
    parser.add_argument('--customer-subdomain', 
                       help='Customer subdomain')
    parser.add_argument('--cloud-provider', default='azure', 
                       help='Cloud provider (aws or azure)')
    parser.add_argument('--airflow-version', default='2.4.2', 
                       help='Airflow version')
    parser.add_argument('--k8s-cluster', 
                       help='Kubernetes cluster name')
    parser.add_argument('--output-file', 
                       help='Output file for environment variables')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    

    
    args = parser.parse_args()
    
    # Create processor
    processor = ConfigProcessor(args.config_file)
    
    # Process configuration
    env_vars = processor.process_configuration(
        branch_name=args.branch_name,
        customer_name=args.customer_name,
        customer_environment=args.customer_environment,
        customer_subdomain=args.customer_subdomain,
        cloud_provider=args.cloud_provider,
        airflow_version=args.airflow_version,
        k8s_cluster=args.k8s_cluster
    )
    
    # Export to GitHub environment
    processor.export_to_github_env(env_vars, args.output_file)
    
    # Print debug info if requested
    if args.debug:
        processor.print_debug_info(env_vars, args.branch_name, args.customer_name)


if __name__ == '__main__':
    main() 
