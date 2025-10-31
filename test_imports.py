#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

try:
    print("Testing imports...")
    
    # Test config import
    import mart_project.resources.config as config
    print("✓ Config import successful")
    
    # Test S3ClientProvider import
    from mart_project.src.main.utility.s3_client_object import S3ClientProvider
    print("✓ S3ClientProvider import successful")
    
    # Test decrypt function import
    from mart_project.src.main.utility.encrypt_decrypt import decrypt
    print("✓ Decrypt function import successful")
    
    # Test logger import
    from mart_project.src.main.utility.logging_config import logger
    print("✓ Logger import successful")
    
    print("\nAll imports successful! The main.py script should now work.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)




