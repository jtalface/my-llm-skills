"""
Sales data pipeline — reads sales.csv, cleans it, aggregates by category and region,
computes statistics, and writes results to output.json.

Exp 4: capitalize() replaces 2-step string build; cache repeated product.title() calls;
        defaultdict for cleaner (and slightly faster) accumulation.
"""

import csv
import json
import time
import math
import os
from collections import defaultdict

DATA_FILE   = os.path.join(os.path.dirname(__file__), 'data', 'sales.csv')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'output.json')

t0 = time.perf_counter()

# Column indices: order_id,customer,product,category,region,amount,quantity,date
COL_PRODUCT  = 2
COL_CATEGORY = 3
COL_REGION   = 4
COL_AMOUNT   = 5
COL_QUANTITY = 6
COL_DATE     = 7

cat_data  = defaultdict(list)
cat_qty   = defaultdict(int)
reg_data  = defaultdict(lambda: [0, 0.0, 0])   # [count, total_rev, total_qty]
prod_rev  = defaultdict(float)
monthly   = defaultdict(float)
total_rev = 0.0
n_orders  = 0

# Cache for repeated string normalizations
prod_cache = {}   # raw → title-cased

with open(DATA_FILE, newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        amount   = float(row[COL_AMOUNT])
        quantity = int(row[COL_QUANTITY])
        revenue  = amount * quantity

        # capitalize() = one call instead of [0].upper() + [1:].lower()
        cat = row[COL_CATEGORY].capitalize()
        reg = row[COL_REGION].capitalize()

        # Cache product title-casing (many duplicates across 100k rows)
        prod_raw = row[COL_PRODUCT]
        prod = prod_cache.get(prod_raw)
        if prod is None:
            prod = prod_raw.title()
            prod_cache[prod_raw] = prod

        ym = row[COL_DATE][:7]

        cat_data[cat].append(revenue)
        cat_qty[cat] += quantity

        rd = reg_data[reg]
        rd[0] += 1
        rd[1] += revenue
        rd[2] += quantity

        prod_rev[prod] += revenue
        monthly[ym]    += revenue
        total_rev      += revenue
        n_orders       += 1

# ── Category stats ─────────────────────────────────────────────────────────────
category_stats = {}
for cat, revenues in cat_data.items():
    n    = len(revenues)
    tot  = sum(revenues)
    mean = tot / n
    variance = sum((x - mean) * (x - mean) for x in revenues) / n
    revenues_sorted = sorted(revenues)
    median = revenues_sorted[n // 2]
    category_stats[cat] = {
        'count':          n,
        'total_revenue':  round(tot, 2),
        'total_qty':      cat_qty[cat],
        'avg_revenue':    round(mean, 2),
        'median_revenue': round(median, 2),
        'std_dev':        round(math.sqrt(variance), 2),
        'min':            round(revenues_sorted[0], 2),
        'max':            round(revenues_sorted[-1], 2),
    }

# ── Region stats ───────────────────────────────────────────────────────────────
region_stats = {
    reg: {
        'count':         rd[0],
        'total_revenue': round(rd[1], 2),
        'total_qty':     rd[2],
    }
    for reg, rd in reg_data.items()
}

# ── Top 10 products ────────────────────────────────────────────────────────────
top_products = [
    {'product': p, 'revenue': round(v, 2)}
    for p, v in sorted(prod_rev.items(), key=lambda x: x[1], reverse=True)[:10]
]

# ── Monthly revenue ────────────────────────────────────────────────────────────
monthly_list = [
    {'month': k, 'revenue': round(v, 2)}
    for k, v in sorted(monthly.items())
]

# ── Output ─────────────────────────────────────────────────────────────────────
output = {
    'generated':       time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'total_orders':    n_orders,
    'total_revenue':   round(total_rev, 2),
    'avg_order_value': round(total_rev / n_orders, 2),
    'categories':      category_stats,
    'regions':         region_stats,
    'top_products':    top_products,
    'monthly_revenue': monthly_list,
}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(output, f, indent=2)

elapsed_ms = (time.perf_counter() - t0) * 1000
print(f"Processed {n_orders:,} orders in {elapsed_ms:.1f}ms → {OUTPUT_FILE}")
