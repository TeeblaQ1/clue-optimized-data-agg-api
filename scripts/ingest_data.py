#!/usr/bin/env python3
"""
Ingest all CSV data: products, regions, then sales.
This ensures proper referential integrity.
"""

import sys
import os
import csv
from psycopg import connect
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def load_products(conn):
    """Load products from CSV into database."""
    with conn.cursor() as cursor:
        print("Loading products...")
        
        # Clear existing products
        cursor.execute("TRUNCATE products RESTART IDENTITY CASCADE")
        
        csv_path = "data/products.csv"
        products_loaded = 0
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO products (id, sku, name)
                    VALUES (%s, %s, %s)
                """, (row['id'], row['sku'], row['name']))
                products_loaded += 1
        
        print(f"Loaded {products_loaded} products")
        return products_loaded

def load_regions(conn):
    """Load regions from CSV into database."""
    with conn.cursor() as cursor:
        print("Loading regions...")
        
        # Clear existing regions
        cursor.execute("TRUNCATE regions RESTART IDENTITY CASCADE")
        
        csv_path = "data/regions.csv"
        regions_loaded = 0
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO regions (id, code, name)
                    VALUES (%s, %s, %s)
                """, (row['id'], row['code'], row['name']))
                regions_loaded += 1
        
        print(f"Loaded {regions_loaded} regions")
        return regions_loaded

def load_sales(conn):
    """Load sales from CSV into database."""
    with conn.cursor() as cursor:
        print("Loading sales...")
        
        # Clear existing sales
        cursor.execute("TRUNCATE sales RESTART IDENTITY CASCADE")
        
        # Create staging table
        cursor.execute("""
            DROP TABLE IF EXISTS sales_stage;
            CREATE TABLE sales_stage (
                sale_date TEXT,
                product_id TEXT,
                region_id TEXT,
                quantity TEXT,
                unit_price TEXT
            );
        """)
        
        # Load CSV into staging
        csv_path = "data/sales.csv"
        rows_inserted = 0
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO sales_stage (sale_date, product_id, region_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (row['sale_date'], row['product_id'], row['region_id'], row['quantity'], row['unit_price']))
                rows_inserted += 1
        
        print(f"Loaded {rows_inserted} rows into staging table")
        
        # Validate and insert into sales
        print("Validating and inserting into sales...")
        
        # Create temporary table for valid rows
        cursor.execute("""
            CREATE TEMP TABLE good_tmp AS
            WITH cleaned AS (
              SELECT
                to_date(sale_date, 'YYYY-MM-DD') AS sale_date,
                (NULLIF(product_id, ''))::INT AS product_id,
                (NULLIF(region_id, ''))::INT AS region_id,
                quantity::INT AS quantity,
                unit_price::INT AS unit_price
              FROM sales_stage
            )
            SELECT *
            FROM cleaned
            WHERE sale_date IS NOT NULL
              AND product_id IS NOT NULL
              AND region_id IS NOT NULL
              AND quantity > 0
              AND unit_price >= 0;
        """)
        
        # Make sure partitions exist for each month
        cursor.execute("""
            DO $$
            DECLARE m_start DATE;
            BEGIN
              FOR m_start IN
                SELECT date_trunc('month', sale_date)::date FROM good_tmp GROUP BY 1
              LOOP
                PERFORM create_month_partition(m_start);
              END LOOP;
            END $$;
        """)
        
        # Insert valid rows into sales
        cursor.execute("""
            INSERT INTO sales (sale_date, product_id, region_id, quantity, unit_price)
            SELECT g.sale_date,
                   p.id,
                   r.id,
                   g.quantity,
                   g.unit_price
            FROM good_tmp g
            JOIN products p ON p.id = g.product_id
            JOIN regions r ON r.id = g.region_id;
        """)
        
        # Get final counts
        cursor.execute("SELECT COUNT(*) as cnt FROM sales")
        sales_count = cursor.fetchone()["cnt"]
        
        cursor.execute("SELECT COUNT(*) as cnt FROM sales_stage")
        staging_count = cursor.fetchone()["cnt"]
        
        print(f"Inserted {sales_count} sales records from {staging_count} staging rows")
        return sales_count

def main():
    """Main ingestion process."""
    print("🚀 Starting complete data ingestion...")
    
    with connect(DB_URL, row_factory=dict_row, autocommit=True) as conn:
        print("Running migrations...")
        with open("migrations/001_init.sql") as f:
            conn.execute(f.read())
        with open("migrations/002_helpers.sql") as f:
            conn.execute(f.read())
        
        # Load in order: products -> regions -> sales
        products_count = load_products(conn)
        regions_count = load_regions(conn)
        sales_count = load_sales(conn)
        
        # Final summary
        print("\n📊 Ingestion Summary:")
        print(f"  Products: {products_count}")
        print(f"  Regions: {regions_count}")
        print(f"  Sales: {sales_count}")
        print("🎉 Complete ingestion finished!")

if __name__ == "__main__":
    main()
