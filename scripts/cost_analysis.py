"""Assumption-based cost model for the README/report.
Change assumptions to match the deployment you would actually buy.
"""
import csv, math
from pathlib import Path

# Illustrative, explicit assumptions—not vendor quotes.
# 384-dimensional float32 vector = 1536 bytes; add 1.5x overhead for metadata/index.
VECTOR_BYTES = 384 * 4
OVERHEAD = 1.5
STORAGE_GB_PER_VECTOR = VECTOR_BYTES * OVERHEAD / (1024**3)
LOCAL_FIXED = 5.00                 # USD/month for a small always-on VM
LOCAL_STORAGE_PER_GB = 0.10        # USD/month
MANAGED_STORAGE_PER_GB = 0.25      # illustrative assumption
MANAGED_OPS_PER_MILLION = 0.05     # illustrative assumption
QUERIES_PER_MONTH = 100_000

rows=[]
for n in [100_000, 1_000_000, 10_000_000]:
    gb = n * STORAGE_GB_PER_VECTOR
    local = LOCAL_FIXED + gb * LOCAL_STORAGE_PER_GB
    managed = gb * MANAGED_STORAGE_PER_GB + (QUERIES_PER_MONTH/1_000_000)*MANAGED_OPS_PER_MILLION
    rows.append([n, round(gb,3), round(local,2), round(managed,2)])
Path("reports").mkdir(exist_ok=True)
with open("reports/cost_comparison.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["vectors","estimated_storage_gb","local_chroma_usd_month","managed_assumption_usd_month"]); w.writerows(rows)
print("reports/cost_comparison.csv")
for r in rows: print(r)
