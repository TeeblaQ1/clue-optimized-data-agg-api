#!/usr/bin/env python3
"""
Script to set up test database environment.
This script helps create and configure the test database for running tests.
"""

import os
import subprocess
import sys
from psycopg import connect
from dotenv import load_dotenv
load_dotenv()

BASE_DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:5433/{os.getenv('POSTGRES_DB')}"

def check_postgres_connection():
    """Check if PostgreSQL is running and accessible"""
    try:
        with connect(BASE_DB_URL) as conn:
            print("Successfully connected to PostgreSQL")
            return True
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running on localhost:5433")
        print("You can start it with: docker-compose up -d db")
        return False

def create_test_database():
    """Create the test database"""
    try:
        with connect(BASE_DB_URL, autocommit=True) as conn:
            # Drop test database if it exists
            conn.execute("DROP DATABASE IF EXISTS test_clue_db")
            # Create new test database
            conn.execute("CREATE DATABASE test_clue_db")
            print("Test database 'test_clue_db' created successfully")
            return True
    except Exception as e:
        print(f"Failed to create test database: {e}")
        return False

def run_migrations():
    """Run database migrations on the test database"""
    try:
        with connect(f"{BASE_DB_URL}/test_clue_db", autocommit=True) as conn:
            with open("migrations/001_init.sql", "r") as f:
                conn.execute(f.read())
            with open("migrations/002_helpers.sql", "r") as f:
                conn.execute(f.read())
        print("Migrations completed successfully")
        return True
    except Exception as e:
        print(f"Failed to run migrations: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up test database environment...")
    
    if not check_postgres_connection():
        sys.exit(1)
    
    if not create_test_database():
        sys.exit(1)
    
    if not run_migrations():
        sys.exit(1)
    
    print("\nTest database setup completed successfully!")
    print("You can now run tests with: pytest")

if __name__ == "__main__":
    main()
