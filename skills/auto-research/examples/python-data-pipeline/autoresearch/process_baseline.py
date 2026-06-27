"""
Sales data pipeline — reads sales.csv, cleans it, aggregates by category and region,
computes statistics, and writes results to output.json.

Deliberately unoptimized:
  - Row-by-row Python loops instead of vectorized pandas operations
  - Re-reads the CSV file multiple times
  - Rebuilds dictionaries on every pass
  - Redundant string operations (re-lowercase, re-strip already-clean data)
  - No use of groupby — manual nested loops for aggregation
  - Sorting done with Python built-ins instead of pandas
  - Multiple unnecessary list comprehensions that could be a single pass
"""

import csv
import json
import time
import math
import os

DATA_FILE   = os.path.join(os.path.dirname(__file__), 'data', 'sales.csv')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'output.json')

t0 = time.perf_counter()

# ── Pass 1: Load all rows into memory ─────────────────────────────────────────
rows = []
with open(DATA_FILE, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# ── Pass 2: Clean and type-cast — row by row with redundant ops ───────────────
cleaned = []
for row in rows:
    # Strip and lowercase everything even though the generator already did it
    order_id  = row['order_id'].strip()
    customer  = row['customer'].strip().title()
    product   = row['product'].strip().title()
    category  = row['category'].strip().lower().strip()   # double strip
    region    = row['region'].strip().lower().strip()
    amount    = float(row['amount'].strip())
    quantity  = int(row['quantity'].strip())
    date_str  = row['date'].strip()

    # Redundant: re-titlecase category and region after lowercasing
    category = category[0].upper() + category[1:]
    region   = region[0].upper() + region[1:]

    # Recompute revenue (already in the CSV but we do it again)
    revenue = amount * quantity

    cleaned.append({
        'order_id': order_id,
        'customer': customer,
        'product':  product,
        'category': category,
        'region':   region,
        'amount':   amount,
        'quantity': quantity,
        'revenue':  revenue,
        'date':     date_str,
    })

# ── Pass 3: Re-read CSV a second time to get unique categories ─────────────────
categories = []
with open(DATA_FILE, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row['category'].strip().lower()
        cat = cat[0].upper() + cat[1:]
        # O(n²) dedup: check if already in list
        already = False
        for existing in categories:
            if existing == cat:
                already = True
                break
        if not already:
            categories.append(cat)
categories.sort()

# ── Pass 4: Re-read CSV a third time to get unique regions ───────────────────
regions = []
with open(DATA_FILE, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        reg = row['region'].strip().lower()
        reg = reg[0].upper() + reg[1:]
        already = False
        for existing in regions:
            if existing == reg:
                already = True
                break
        if not already:
            regions.append(reg)
regions.sort()

# ── Pass 5: Aggregate by category — manual loops instead of groupby ───────────
category_stats = {}
for cat in categories:
    # Filter to this category (full scan for every category)
    subset = [r for r in cleaned if r['category'] == cat]
    total_revenue = 0.0
    total_qty     = 0
    amounts       = []
    for r in subset:
        total_revenue += r['revenue']
        total_qty     += r['quantity']
        amounts.append(r['revenue'])
    n = len(amounts)
    if n == 0:
        continue
    mean = total_revenue / n
    # Compute std dev manually
    variance = sum((x - mean) ** 2 for x in amounts) / n
    std_dev  = math.sqrt(variance)
    amounts_sorted = sorted(amounts)
    median = amounts_sorted[n // 2]
    category_stats[cat] = {
        'count':         n,
        'total_revenue': round(total_revenue, 2),
        'total_qty':     total_qty,
        'avg_revenue':   round(mean, 2),
        'median_revenue':round(median, 2),
        'std_dev':       round(std_dev, 2),
        'min':           round(min(amounts), 2),
        'max':           round(max(amounts), 2),
    }

# ── Pass 6: Aggregate by region — same manual approach ───────────────────────
region_stats = {}
for reg in regions:
    subset = [r for r in cleaned if r['region'] == reg]
    total_revenue = 0.0
    total_qty     = 0
    for r in subset:
        total_revenue += r['revenue']
        total_qty     += r['quantity']
    region_stats[reg] = {
        'count':         len(subset),
        'total_revenue': round(total_revenue, 2),
        'total_qty':     total_qty,
    }

# ── Pass 7: Top 10 products by revenue — manual sort ─────────────────────────
product_revenue = {}
for r in cleaned:
    p = r['product']
    if p not in product_revenue:
        product_revenue[p] = 0.0
    product_revenue[p] += r['revenue']

# Sort products manually (bubble sort for extra pain)
product_list = list(product_revenue.items())
for i in range(len(product_list)):
    for j in range(len(product_list) - 1 - i):
        if product_list[j][1] < product_list[j + 1][1]:
            product_list[j], product_list[j + 1] = product_list[j + 1], product_list[j]

top_products = [{'product': p, 'revenue': round(v, 2)} for p, v in product_list[:10]]

# ── Pass 8: Monthly revenue — string-based date parsing ──────────────────────
monthly = {}
for r in cleaned:
    # Parse YYYY-MM-DD manually instead of using datetime
    parts  = r['date'].split('-')
    ym_key = f"{parts[0]}-{parts[1]}"
    if ym_key not in monthly:
        monthly[ym_key] = 0.0
    monthly[ym_key] += r['revenue']

monthly_sorted = sorted(monthly.items())
monthly_list   = [{'month': k, 'revenue': round(v, 2)} for k, v in monthly_sorted]

# ── Overall stats ─────────────────────────────────────────────────────────────
all_revenues = [r['revenue'] for r in cleaned]
total        = sum(all_revenues)
overall_mean = total / len(all_revenues)

output = {
    'generated':      time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'total_orders':   len(cleaned),
    'total_revenue':  round(total, 2),
    'avg_order_value':round(overall_mean, 2),
    'categories':     category_stats,
    'regions':        region_stats,
    'top_products':   top_products,
    'monthly_revenue':monthly_list,
}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(output, f, indent=2)

elapsed_ms = (time.perf_counter() - t0) * 1000
print(f"Processed {len(cleaned):,} orders in {elapsed_ms:.1f}ms → {OUTPUT_FILE}")
