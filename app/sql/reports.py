MONTHLY_SALES = """
SELECT to_char(date_trunc('month', s.sale_date), 'YYYY-MM') AS month,
       SUM(s.quantity * s.unit_price)::bigint AS total_revenue,
       SUM(s.quantity)::bigint AS total_quantity
FROM sales s
JOIN products p ON p.id = s.product_id
JOIN regions  r ON r.id = s.region_id
WHERE s.sale_date >= %(start)s
  AND s.sale_date <  %(end)s
  AND (%(sku)s = '' OR p.sku = %(sku)s)
  AND (%(region)s = '' OR r.code = %(region)s)
GROUP BY month
ORDER BY month;
"""

TOP_PRODUCTS = """
SELECT p.sku AS product_sku,
       p.name AS product_name,
       SUM(s.quantity * s.unit_price)::bigint AS total_revenue,
       SUM(s.quantity)::bigint AS total_quantity
FROM sales s
JOIN products p ON p.id = s.product_id
JOIN regions  r ON r.id = s.region_id
WHERE s.sale_date >= %(start)s
  AND s.sale_date <  %(end)s
  AND (%(region)s = '' OR r.code = %(region)s)
GROUP BY p.sku, p.name
ORDER BY total_revenue DESC
LIMIT %(limit)s;
"""
