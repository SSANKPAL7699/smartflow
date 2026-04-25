# data/simulated/generate_data.py
# Simulates 4 SAP tables: LFA1, MARA, EKKO, RBKP
# No real SAP credentials needed!

import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

# ── Setup ────────────────────────────────────────────────────
fake = Faker()
random.seed(42)       # Same data every run (reproducible)
np.random.seed(42)

OUTPUT_DIR = os.path.dirname(__file__)  # saves CSVs in data/simulated/
NUM_VENDORS   = 50
NUM_MATERIALS = 100
NUM_POS       = 200   # Purchase Orders
NUM_INVOICES  = 180   # Invoices (not all POs get invoiced)

# ── TABLE 1: LFA1 — Vendor Master ────────────────────────────
# In real SAP: stores supplier info (name, country, payment terms)
def generate_lfa1():
    vendors = []
    for i in range(NUM_VENDORS):
        vendors.append({
            "LIFNR": f"V{str(i+1).zfill(5)}",        # Vendor number e.g. V00001
            "NAME1": fake.company(),                   # Company name
            "LAND1": random.choice(["US","IN","DE",
                                    "GB","JP","CN"]),  # Country code
            "ORT01": fake.city(),                      # City
            "PSTLZ": fake.postcode(),                  # Postal code
            "LIFSP": random.choice(["", "", "X"]),     # Blocked? X=yes (mostly empty)
            "KTOKK": random.choice(["LIFA","LIFB"]),   # Vendor account group
            "CREATED_ON": fake.date_between(
                start_date="-5y", end_date="-1y"
            ).strftime("%Y-%m-%d"),
        })
    df = pd.DataFrame(vendors)
    path = os.path.join(OUTPUT_DIR, "lfa1.csv")
    df.to_csv(path, index=False)
    print(f"✅ LFA1 (Vendors):    {len(df)} records → {path}")
    return df

# ── TABLE 2: MARA — Material Master ──────────────────────────
# In real SAP: stores product/material info (type, unit, weight)
def generate_mara():
    material_types = ["ROH","HALB","FERT","HAWA"]
    # ROH=Raw, HALB=Semi-finished, FERT=Finished, HAWA=Trading goods
    units = ["KG", "EA", "LT", "MT", "PC"]

    materials = []
    for i in range(NUM_MATERIALS):
        mat_type = random.choice(material_types)
        materials.append({
            "MATNR": f"MAT{str(i+1).zfill(6)}",      # Material number
            "MAKTX": fake.bs().title()[:40],           # Material description
            "MTART": mat_type,                         # Material type
            "MEINS": random.choice(units),             # Base unit of measure
            "MATKL": f"GRP{random.randint(1,10):02d}", # Material group
            "NTGEW": round(random.uniform(0.1, 500), 2), # Net weight
            "GEWEI": "KG",                             # Weight unit
            "CREATED_ON": fake.date_between(
                start_date="-5y", end_date="-1y"
            ).strftime("%Y-%m-%d"),
        })
    df = pd.DataFrame(materials)
    path = os.path.join(OUTPUT_DIR, "mara.csv")
    df.to_csv(path, index=False)
    print(f"✅ MARA (Materials):  {len(df)} records → {path}")
    return df

# ── TABLE 3: EKKO — Purchase Order Header ────────────────────
# In real SAP: stores PO header info (vendor, date, total value)
def generate_ekko(lfa1_df):
    vendor_ids = lfa1_df["LIFNR"].tolist()
    po_types   = ["NB", "ZUB", "FO"]
    # NB=Standard PO, ZUB=Stock transfer, FO=Framework order
    currencies = ["USD", "EUR", "GBP", "INR"]

    pos = []
    base_date = datetime(2023, 1, 1)

    for i in range(NUM_POS):
        po_date = base_date + timedelta(days=random.randint(0, 730))
        net_value = round(random.uniform(1000, 500000), 2)
        pos.append({
            "EBELN": f"PO{str(4500000+i)}",            # PO number
            "LIFNR": random.choice(vendor_ids),        # Vendor (FK → LFA1)
            "BSART": random.choice(po_types),          # PO type
            "BEDAT": po_date.strftime("%Y-%m-%d"),     # PO date
            "WAERS": random.choice(currencies),        # Currency
            "NETWR": net_value,                        # Net value
            "EKGRP": f"EG{random.randint(1,5):02d}",  # Purchasing group
            "ZTERM": random.choice(["NET30","NET60",
                                    "NET90","IMMEDIATE"]), # Payment terms
            "STATUS": random.choice(["OPEN","APPROVED",
                                     "CLOSED","CANCELLED"]),
        })
    df = pd.DataFrame(pos)
    path = os.path.join(OUTPUT_DIR, "ekko.csv")
    df.to_csv(path, index=False)
    print(f"✅ EKKO (Purchase Orders): {len(df)} records → {path}")
    return df

# ── TABLE 4: RBKP — Invoice Header ───────────────────────────
# In real SAP: stores vendor invoice info (amount, tax, status)
def generate_rbkp(ekko_df):
    po_numbers = ekko_df["EBELN"].tolist()
    # Only 90% of POs get invoiced (realistic!)
    invoiced_pos = random.sample(po_numbers, NUM_INVOICES)

    invoices = []
    base_date = datetime(2023, 2, 1)

    for i, po_num in enumerate(invoiced_pos):
        po_row    = ekko_df[ekko_df["EBELN"] == po_num].iloc[0]
        inv_date  = base_date + timedelta(days=random.randint(0, 700))
        gross_amt = round(po_row["NETWR"] * random.uniform(0.95, 1.05), 2)
        tax_amt   = round(gross_amt * random.uniform(0.05, 0.20), 2)

        invoices.append({
            "BELNR": f"INV{str(5100000+i)}",           # Invoice number
            "EBELN": po_num,                            # PO reference (FK → EKKO)
            "BLDAT": inv_date.strftime("%Y-%m-%d"),    # Invoice date
            "WAERS": po_row["WAERS"],                  # Currency (same as PO)
            "RMWWR": gross_amt,                        # Gross invoice amount
            "WMWST": tax_amt,                          # Tax amount
            "NETWR": round(gross_amt - tax_amt, 2),   # Net amount
            "ZLSPR": random.choice(["", "", "", "A"]), # Payment block (A=blocked)
            "RBSTAT": random.choice(["POSTED","PENDING",
                                     "CANCELLED","PARKED"]),
        })
    df = pd.DataFrame(invoices)
    path = os.path.join(OUTPUT_DIR, "rbkp.csv")
    df.to_csv(path, index=False)
    print(f"✅ RBKP (Invoices):   {len(df)} records → {path}")
    return df

# ── Main: Generate All Tables ────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 Generating simulated SAP data...\n")
    lfa1 = generate_lfa1()
    mara = generate_mara()
    ekko = generate_ekko(lfa1)
    rbkp = generate_rbkp(ekko)
    print("\n📊 Sample Vendor:")
    print(lfa1.head(2).to_string())
    print("\n📊 Sample Purchase Order:")
    print(ekko.head(2).to_string())
    print("\n✅ All SAP tables generated successfully!")