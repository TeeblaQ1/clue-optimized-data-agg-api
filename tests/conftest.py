import os
import pytest
import subprocess
import time
from psycopg import connect
from dotenv import load_dotenv

load_dotenv()

# Test database configuration
TEST_DB_NAME = "test_clue_db"
TEST_DB_USER = os.getenv("POSTGRES_USER")
TEST_DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
TEST_DB_HOST = os.getenv("POSTGRES_HOST")
TEST_DB_PORT = os.getenv("POSTGRES_PORT", 5432)

# Base connection string for creating/dropping databases
BASE_DB_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
print(f"Base DB URL: {BASE_DB_URL}")

# Test database connection string
TEST_DB_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

def create_test_database():
    """Create a temporary test database"""
    try:
        with connect(BASE_DB_URL, autocommit=True) as conn:
            # Drop database if it exists
            conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
            # Create new test database
            conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
        print(f"Created test database: {TEST_DB_NAME}")
    except Exception as e:
        print(f"Error creating test database: {e}")
        raise

def drop_test_database():
    """Drop the temporary test database"""
    try:
        with connect(BASE_DB_URL, autocommit=True) as conn:
            # Terminate all connections to the test database
            conn.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid()
            """)
            # Drop the test database
            conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        print(f"Dropped test database: {TEST_DB_NAME}")
    except Exception as e:
        print(f"Error dropping test database: {e}")

def run_migrations():
    """Run database migrations on the test database"""
    try:
        with connect(TEST_DB_URL, autocommit=True) as conn:
            # Read and execute migration files
            with open("migrations/001_init.sql", "r") as f:
                conn.execute(f.read())
            with open("migrations/002_helpers.sql", "r") as f:
                conn.execute(f.read())
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise

@pytest.fixture(scope="session")
def test_db():
    """Fixture to create and manage test database lifecycle"""
    # Create test database
    create_test_database()
    
    # Wait a moment for database to be ready
    time.sleep(1)
    
    # Run migrations
    run_migrations()
    
    # Yield the test database URL
    yield TEST_DB_URL
    
    # Clean up: drop test database
    drop_test_database()

@pytest.fixture
def db_connection(test_db):
    """Fixture providing a database connection for individual tests"""
    with connect(test_db, autocommit=True) as conn:
        yield conn

@pytest.fixture
def clean_db(test_db):
    """Fixture to clean all data between tests"""
    with connect(test_db, autocommit=True) as conn:
        # Get all table names
        result = conn.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """)
        tables = [row[0] for row in result.fetchall()]
        
        # Truncate all tables to clean data
        if tables:
            conn.execute(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE")
        
        yield test_db
