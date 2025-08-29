-- create simple products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL DEFAULT ''
);

-- create simple regions table
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL DEFAULT ''
);

-- Partitioned fact table
-- without partitioning, the monthly sales report would be much slower
CREATE TABLE IF NOT EXISTS sales (
    id BIGSERIAL,
    sale_date DATE NOT NULL,
    product_id INT NOT NULL REFERENCES products(id),
    region_id INT NOT NULL REFERENCES regions(id),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    unit_price BIGINT NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (id, sale_date)
) PARTITION BY RANGE (sale_date);
