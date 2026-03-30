#!/usr/bin/env python3
"""
Test script for the Jinja2 configuration processor.
This script demonstrates how the configuration system works with different branches and environments.
"""

import os
import sys
sys.path.append('scripts')
from config_processor import ConfigProcessor

def test_configuration():
    """Test the configuration processor with different scenarios."""
    
    # Test scenarios
    test_cases = [
        {
            'name': 'Main branch - Production EU',
            'branch_name': 'main',
            'customer_name': 'AcmeCorp',
            'customer_environment': 'prod-eu',
            'customer_subdomain': 'prod',
            'cloud_provider': 'azure',
            'airflow_version': '2.4.2'
        },
        {
            'name': 'Dev branch - Development',
            'branch_name': 'dev',
            'customer_name': 'AcmeCorp',
            'customer_environment': 'dev',
            'customer_subdomain': 'dev',
            'cloud_provider': 'azure',
            'airflow_version': '2.4.2'
        },
        {
            'name': 'Feature branch - Development',
            'branch_name': 'feature-user-auth',
            'customer_name': 'AcmeCorp',
            'customer_environment': 'dev',
            'customer_subdomain': 'dev',
            'cloud_provider': 'azure',
            'airflow_version': '2.4.2'
        },
        {
            'name': 'Main branch - Production US (AWS)',
            'branch_name': 'main',
            'customer_name': 'TechCorp',
            'customer_environment': 'prod-us',
            'customer_subdomain': 'prod',
            'cloud_provider': 'aws',
            'airflow_version': '2.4.2'
        },
        {
            'name': 'BootsBlue branch - Production EU',
            'branch_name': 'bootsblue',
            'customer_name': 'Boots',
            'customer_environment': 'prod-eu',
            'customer_subdomain': 'prod',
            'cloud_provider': 'azure',
            'airflow_version': '2.4.2'
        }
    ]
    
    processor = ConfigProcessor()
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {test_case['name']}")
        print('='*60)
        
        try:
            # Process configuration
            env_vars = processor.process_configuration(**test_case)
            
            # Print key results
            print(f"Branch: {test_case['branch_name']}")
            print(f"Customer: {test_case['customer_name']}")
            print(f"Environment: {test_case['customer_environment']}")
            print(f"Cloud Provider: {test_case['cloud_provider']}")
            print()
            
            # Print important environment variables
            key_vars = [
                'INPUT_BUCKET_NAME', 'OUTPUT_BUCKET_NAME', 'DATASTORE_BUCKET_NAME',
                'MAPS_DATABASE_SECRET_ID', 'POKEDEX_ENVIRONMENT', 'ROCKS_ENV',
                'K8S_NAMESPACE', 'IMAGE_ENV', 'CUSTOMER_SUBDOMAIN', 'LOG_LEVEL'
            ]
            
            print("📋 Key Configuration Variables:")
            for var in key_vars:
                value = env_vars.get(var, 'Not set')
                print(f"  {var}: {value}")
            
            # Print resource limits if they exist
            if 'RESOURCE_LIMITS' in env_vars:
                print(f"  RESOURCE_LIMITS: {env_vars['RESOURCE_LIMITS']}")
            
            # Check for computed values
            print(f"\n🔍 Computed Values:")
            print(f"  K8S_CLUSTER: {env_vars.get('K8S_CLUSTER', 'Not set')}")
            print(f"  K8S_CLUSTER_RG: {env_vars.get('K8S_CLUSTER_RG', 'Not set')}")
            
        except Exception as e:
            print(f"❌ Error processing configuration: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("✅ Configuration testing completed!")
    print('='*60)

if __name__ == '__main__':
    test_configuration() 
