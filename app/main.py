from fastapi import FastAPI, Query
from app.cache import cached_report
from app.models import MonthlySalesResponse, MonthRow, TopProductsResponse, TopProductRow
from app.sql import reports
from typing import Optional

app = FastAPI(title="Optimized Data Aggregation API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

def run_query(sql: str, params: dict = None):
    from app.db import get_conn
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

@cached_report
def cached_run_query(*, sql: str, params: dict):
    return run_query(sql, params)

@app.get("/reports/monthly-sales", response_model=MonthlySalesResponse)
def monthly_sales(
    start_date: str = Query(..., description="Start date in YYYY-MM-01 format"),
    end_date: str = Query(..., description="End date in YYYY-MM-01 format"),
    product_sku: Optional[str] = Query(None, description="Optional product SKU filter"),
    region_code: Optional[str] = Query(None, description="Optional region code filter")
):
    params = {
        "start": start_date,
        "end": end_date,
        "sku": product_sku or "",
        "region": region_code or ""
    }
    rows = cached_run_query(sql=reports.MONTHLY_SALES, params=params)
    return MonthlySalesResponse(rows=[MonthRow(**r) for r in rows])

@app.get("/reports/top-products", response_model=TopProductsResponse)
def top_products(
    start_date: str = Query(..., description="Start date in YYYY-MM-01 format"),
    end_date: str = Query(..., description="End date in YYYY-MM-01 format"),
    region_code: Optional[str] = Query(None, description="Optional region code filter"),
    limit: int = Query(default=5, ge=1, le=50, description="Number of top products to return (1-50)")
):
    params = {
        "start": start_date,
        "end": end_date,
        "region": region_code or "",
        "limit": limit
    }
    rows = cached_run_query(sql=reports.TOP_PRODUCTS, params=params)
    return TopProductsResponse(rows=[TopProductRow(**r) for r in rows])
