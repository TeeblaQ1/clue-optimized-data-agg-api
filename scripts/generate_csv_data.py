#!/usr/bin/env python3
"""
Generate CSV data files for products, regions, and sales.
Usage: python scripts/generate_csv_data.py --products_count 20 --sales_count 5000
"""

import sys
import csv
import random
import argparse
from datetime import datetime, timedelta
import os

def generate_products(num_products):
    """Generate product data with realistic names."""
    products = []
    product_types = [
        'Excavator', 'Bulldozer', 'Crane', 'Dump Truck', 'Loader', 'Backhoe', 'Concrete Mixer',
        'Forklift', 'Grader', 'Compactor', 'Scissor Lift', 'Skid Steer', 'Paver', 'Drill Rig'
    ]
    categories = [
        'Standard', 'Heavy Duty', 'Compact', 'Hydraulic', 'Electric', 'Tracked', 'Wheeled', 'All-Terrain'
    ]
    
    for i in range(1, num_products + 1):
        product_type = random.choice(product_types)
        category = random.choice(categories)
        name = f"{category} {product_type} {i:03d}"
        sku = f"{product_type[:3].upper()}{i:03d}"
        
        products.append({
            'id': i,
            'sku': sku,
            'name': name
        })
    
    return products

def generate_regions():
    """Generate region data with realistic codes and names."""
    regions = []

    world_regions = [
        {'name': 'Africa', 'code': 'AF'},
        {'name': 'Asia', 'code': 'AS'},
        {'name': 'Europe', 'code': 'EU'},
        {'name': 'North America', 'code': 'NA'},
        {'name': 'Oceania', 'code': 'OC'},
        {'name': 'South America', 'code': 'SA'},
        {'name': 'Antarctica', 'code': 'AN'}
    ]

    for i in range(1, len(world_regions) + 1):
        region = world_regions[i-1]
        name = region['name']
        code = region['code']

        regions.append({
            'id': i,
            'code': code,
            'name': name
        })
    return regions

def generate_sales(num_sales, products, regions):
    """Generate sales data with realistic patterns."""
    sales = []
    
    # Generate dates for the last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    for i in range(num_sales):
        # Random date within range
        random_days = random.randint(0, (end_date - start_date).days)
        sale_date = start_date + timedelta(days=random_days)
        
        # Random product and region
        product = random.choice(products)
        region = random.choice(regions)
        
        # Realistic quantities and prices
        quantity = random.randint(1, 100)
        unit_price = random.randint(500, 5000)
        
        sales.append({
            'sale_date': sale_date.strftime('%Y-%m-%d'),
            'product_id': product['id'],
            'region_id': region['id'],
            'quantity': quantity,
            'unit_price': unit_price
        })
    
    return sales

def save_csv(data, filename, fieldnames):
    """Save data to CSV file."""
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filepath} with {len(data)} rows")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate CSV data files for products, regions, and sales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python scripts/generate_csv_data.py --products_count 20 --sales_count 5000
        python scripts/generate_csv_data.py -p 50 -s 10000
        python scripts/generate_csv_data.py --products_count 100
                """
            )
    
    parser.add_argument(
        '--products_count', '-p',
        type=int,
        default=10,
        help='Number of products to generate (default: 10)'
    )
    
    parser.add_argument(
        '--sales_count', '-s',
        type=int,
        default=1000,
        help='Number of sales records to generate (default: 1000)'
    )
    
    args = parser.parse_args()
    
    print(f"Generating CSV data:")
    print(f"  Products: {args.products_count}")
    print(f"  Sales: {args.sales_count}")
    print()
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Generate and save products, regions and sales
    products = generate_products(args.products_count)
    save_csv(products, 'products.csv', ['id', 'sku', 'name'])
    
    regions = generate_regions()
    save_csv(regions, 'regions.csv', ['id', 'code', 'name'])
    
    sales = generate_sales(args.sales_count, products, regions)
    save_csv(sales, 'sales.csv', ['sale_date', 'product_id', 'region_id', 'quantity', 'unit_price'])
    
    print(f"\n All CSV files generated successfully in the data/ folder!")

if __name__ == "__main__":
    main()
