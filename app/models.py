from pydantic import BaseModel, Field
from typing import Optional, List

class MonthRow(BaseModel):
    month: str
    total_revenue: int
    total_quantity: int

class MonthlySalesResponse(BaseModel):
    rows: List[MonthRow]

class TopProductRow(BaseModel):
    product_sku: str
    product_name: str
    total_revenue: int
    total_quantity: int

class TopProductsResponse(BaseModel):
    rows: List[TopProductRow]
