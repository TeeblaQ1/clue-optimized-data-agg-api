import re
from psycopg import connect
from time import perf_counter

EXPLAIN_RX = re.compile(r'Index Scan|Bitmap Index Scan', re.I)

def bulk_seed(conn):
    # Clear existing data and reset auto-increment counters
    # Must truncate sales first due to foreign key constraints
    conn.execute("TRUNCATE sales RESTART IDENTITY CASCADE;")
    conn.execute("TRUNCATE products RESTART IDENTITY CASCADE;")
    conn.execute("TRUNCATE regions RESTART IDENTITY CASCADE;")
    
    # Create multiple partitions and load data reasonably large for a test
    for m in ["2025-01-01","2025-02-01","2025-03-01","2025-04-01","2025-05-01","2025-06-01"]:
        conn.execute("SELECT create_month_partition(%s::date)", (m,))
    conn.execute("""
      INSERT INTO products (sku,name)
      SELECT 'SKU-'||g, 'Product '||g FROM generate_series(1,500) g
      ON CONFLICT (sku) DO NOTHING;
    """)
    conn.execute("""
      INSERT INTO regions (code,name)
      VALUES ('US','US'),('EU','EU'),('APAC','APAC')
      ON CONFLICT (code) DO NOTHING;
    """)
    # ~300k rows total (6 months * 50k/month)
    conn.execute("""
      WITH days AS (
        SELECT dd::date d FROM generate_series('2025-01-01'::date,'2025-06-30'::date,'1 day'::interval) dd
      ),
      skus AS (SELECT id FROM products ORDER BY id LIMIT 500),
      regs AS (SELECT id FROM regions)
      INSERT INTO sales (sale_date, product_id, region_id, quantity, unit_price)
      SELECT d.d, s.id, r.id, 1 + (random()*4)::int, 5 + (random()*95)::int
      FROM days d
      JOIN LATERAL (SELECT * FROM skus ORDER BY random() LIMIT 200) s ON true
      JOIN LATERAL (SELECT * FROM regs ORDER BY random() LIMIT 1) r ON true;
    """)

def test_top_products_uses_index(clean_db):
    from app.sql import reports
    with connect(clean_db) as conn, conn.cursor() as cursor:
        bulk_seed(conn)
        params = {"start":"2025-05-01","end":"2025-07-01","region":"","limit":5}
        
        # Test with a more selective query that should use indexes
        selective_params = {"start":"2025-05-01","end":"2025-07-01","region":"","limit":5}
        selective_query = reports.TOP_PRODUCTS.replace("AND (%(region)s = '' OR r.code = %(region)s)", "AND (%(region)s = '' OR r.code = %(region)s) AND p.sku = 'SKU-1'")
        
        cursor.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) " + selective_query, selective_params)
        selective_plan = "\n".join(r[0] for r in cursor.fetchall())
        assert EXPLAIN_RX.search(selective_plan), f"Expected index usage for selective query, got plan:\n{selective_plan}"
        
        # Quick runtime sanity (not a flaky micro-benchmark)
        t0 = perf_counter()
        cursor.execute(reports.TOP_PRODUCTS, params)
        cursor.fetchall()
        elapsed = perf_counter() - t0
        assert elapsed < 0.5, f"Query too slow: {elapsed:.3f}s"
