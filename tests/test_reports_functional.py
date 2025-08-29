from psycopg import connect
from app.sql import reports

def seed_small(conn):
    # Clear existing data and reset auto-increment counters
    # Must truncate sales first due to foreign key constraints
    conn.execute("TRUNCATE sales RESTART IDENTITY CASCADE;")
    conn.execute("TRUNCATE products RESTART IDENTITY CASCADE;")
    conn.execute("TRUNCATE regions RESTART IDENTITY CASCADE;")
    
    conn.execute("SELECT create_month_partition('2025-06-01'::date)")
    conn.execute("""
      INSERT INTO products (sku,name) VALUES
        ('A','A'), ('B','B')
      ON CONFLICT (sku) DO NOTHING;
    """)
    conn.execute("""
      INSERT INTO regions (code,name) VALUES
        ('US','US'), ('EU','EU')
      ON CONFLICT (code) DO NOTHING;
    """)
    conn.execute("""
      INSERT INTO sales (sale_date, product_id, region_id, quantity, unit_price)
      SELECT d::date, p.id, r.id, 2, 10.00
      FROM generate_series('2025-06-01','2025-06-15', interval '1 day') d
      CROSS JOIN LATERAL (SELECT id FROM products WHERE sku='A') p
      CROSS JOIN LATERAL (SELECT id FROM regions WHERE code='US') r;
    """)

def test_monthly_report(clean_db):
    with connect(clean_db) as conn:
        seed_small(conn)
        with conn.cursor() as cursor:
            cursor.execute(reports.MONTHLY_SALES, {"start":"2025-06-01","end":"2025-07-01","sku":"","region":""})
            rows = cursor.fetchall()
            assert rows[0][0] == "2025-06"
            # total revenue: 15 days * 2 qty * 10.00 = 300.00
            assert float(rows[0][1]) == 300.0
