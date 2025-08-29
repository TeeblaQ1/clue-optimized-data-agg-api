# Clue Optimized Data Aggregation API

A FastAPI-based data aggregation service with PostgreSQL backend and optimized reporting capabilities.

## Quick Start

### 1. Start the Services

```bash
docker compose up -d
```

### 2. Generate Sample Data

Generate CSV files for products, regions, and sales:

```bash
# Generate with default sizes (10 products, 1000 sales)
docker compose exec api python scripts/generate_csv_data.py

# Generate with custom sizes
docker compose exec api python scripts/generate_csv_data.py --products_count 20 --sales_count 5000
```

This creates:
- `data/products.csv` - Product data (id, sku, name)
- `data/regions.csv` - Region data (id, code, name)  
- `data/sales.csv` - Sales data (sale_date, product_id, region_id, quantity, unit_price)

The regions are fixed to the following:
world_regions = [
    {'name': 'Africa', 'code': 'AF'},
    {'name': 'Asia', 'code': 'AS'},
    {'name': 'Europe', 'code': 'EU'},
    {'name': 'North America', 'code': 'NA'},
    {'name': 'Oceania', 'code': 'OC'},
    {'name': 'South America', 'code': 'SA'},
    {'name': 'Antarctica', 'code': 'AN'}
]

### 3. Ingest Data

Loads products and regions first, then sales for proper referential integrity:

```bash
docker compose exec api python scripts/ingest_data.py
```


### 4. Access the API
- **Health Check**: http://localhost:8000/health
- **Monthly Sale Summary Reports**: http://localhost:8000/reports/monthly-sales?start_date=2025-01-01&end_date=2025-07-01&product_sku=&region_code=
- **Top Products By Revenue Reports**: http://localhost:8000/reports/top-products?start_date=2025-01-01&end_date=2025-07-01&limit=5&region_code=

## Data Schema

### Products
- `id`: Primary key
- `sku`: Unique product identifier
- `name`: Product name

### Regions  
- `id`: Primary key
- `code`: Region code (e.g., "NA" for North America)
- `name`: Region name

### Sales
- `sale_date`: Date of sale (YYYY-MM-DD)
- `product_id`: Foreign key to products.id
- `region_id`: Foreign key to regions.id
- `quantity`: Number of units sold
- `unit_price`: Price per unit (this is set to integer to represent the samllest unit of currency and avoid floating point precision errors)

## Scripts

### `scripts/generate_csv_data.py`
Generates realistic sample data with configurable row counts.

**Usage:**
```bash
docker compose exec api python scripts/generate_csv_data.py -- products_count [num_products] --sales_count [num_sales]
```

### `scripts/ingest_data.py`
Complete data ingestion pipeline that loads products, regions, and sales in the correct order.
**Usage:**
```bash
docker compose exec api python scripts/ingest_data.py
```

## Development

### Running Tests

The test suite uses a dedicated test database that is automatically created and destroyed for each test session. This ensures tests don't interfere with your development database.

**Prerequisites:**
1. Make sure PostgreSQL is running: `docker compose up -d db`
2. The test database will be created automatically when running tests

**Run Tests:**
```bash
# Run all tests
docker compose exec api pytest

# Run with verbose output
docker compose exec api pytest -v

# Run specific test file
docker compose exec api pytest tests/test_reports_functional.py

# Run tests with coverage
docker compose exec api pytest --cov=app
```

**Test Database Setup:**
If you need to manually set up the test database:
```bash
docker compose exec api python scripts/setup_test_db.py
```

### Database Migrations

Migrations are automatically run during ingestion, but can be run manually:

## Architecture

- **Partitioned Tables**: Sales data is partitioned by month for performance
- **Materialized Views**: Pre-computed aggregations for fast reporting
- **Connection Pooling**: Efficient database connection management
- **Caching**: Redis-based caching for frequently accessed data

## Troubleshooting

### Common Issues

1. **CSV Format Issues**: Ensure CSV headers match expected schema exactly
2. **Database Connection**: Check that PostgreSQL is running and accessible

### Data Validation

The ingestion scripts validate:
- Date format (YYYY-MM-DD)
- Numeric quantities and prices
- Referential integrity (product_id, region_id exist)
- Data completeness (no null required fields)
