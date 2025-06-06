#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    """Run InfluxDB AWS tests"""
    print("Starting InfluxDB AWS Tests...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found. Please create it with your InfluxDB and AWS configuration.")
        sys.exit(1)
    
    # Run pytest
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'test_influxdb_aws.py', 
            '-v', 
            '--tb=short'
        ], check=True)
        print("All tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
