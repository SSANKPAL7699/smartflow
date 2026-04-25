import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config import settings
from backend.models.vendor import VendorDB
from backend.models.material import MaterialDB
from backend.models.purchase_order import PurchaseOrderDB
from backend.models.invoice import InvoiceDB


def extract(table_name: str) -> pd.DataFrame:
    path = os.path.join(settings.DATA_DIR, f"{table_name}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"SAP table file not found: {path}")
    df = pd.read_csv(path)
    print(f"  📥 Extracted {len(df)} rows from {table_name.upper()}")
    return df


def transform_lfa1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["NAME1"] = df["NAME1"].str.strip().str.title()
    df["LAND1"] = df["LAND1"].str.upper().str[:3]
    df["LIFSP"] = df["LIFSP"].fillna("")
    df["KTOKK"] = df["KTOKK"].fillna("LIFA")
    df["CREATED_ON"] = pd.to_datetime(df["CREATED_ON"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.drop_duplicates(subset=["LIFNR"])
    print(f"  🔄 Transformed LFA1: {len(df)} vendors")
    return df


def transform_mara(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MAKTX"] = df["MAKTX"].str.strip().str[:40]
    df["MTART"] = df["MTART"].fillna("ROH")
    df["MEINS"] = df["MEINS"].fillna("EA")
    df["NTGEW"] = pd.to_numeric(df["NTGEW"], errors="coerce").fillna(0.0)
    df["CREATED_ON"] = pd.to_datetime(df["CREATED_ON"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.drop_duplicates(subset=["MATNR"])
    print(f"  🔄 Transformed MARA: {len(df)} materials")
    return df


def transform_ekko(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["NETWR"] = pd.to_numeric(df["NETWR"], errors="coerce").fillna(0.0)
    df["WAERS"] = df["WAERS"].fillna("USD")
    df["STATUS"] = df["STATUS"].fillna("OPEN")
    df["BEDAT"] = pd.to_datetime(df["BEDAT"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.drop_duplicates(subset=["EBELN"])
    print(f"  🔄 Transformed EKKO: {len(df)} purchase orders")
    return df


def transform_rbkp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["RMWWR"] = pd.to_numeric(df["RMWWR"], errors="coerce").fillna(0.0)
    df["WMWST"] = pd.to_numeric(df["WMWST"], errors="coerce").fillna(0.0)
    df["NETWR"] = pd.to_numeric(df["NETWR"], errors="coerce").fillna(0.0)
    df["ZLSPR"] = df["ZLSPR"].fillna("")
    df["RBSTAT"] = df["RBSTAT"].fillna("PENDING")
    df["BLDAT"] = pd.to_datetime(df["BLDAT"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.drop_duplicates(subset=["BELNR"])
    print(f"  🔄 Transformed RBKP: {len(df)} invoices")
    return df


async def load_table(db: AsyncSession, df: pd.DataFrame, model_class, pk_field: str):
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        pk_value = row[pk_field]
        existing = await db.get(model_class, pk_value)
        if existing:
            skipped += 1
            continue
        record = model_class(**row.to_dict())
        db.add(record)
        inserted += 1
    await db.commit()
    print(f"  💾 Loaded {model_class.__tablename__}: {inserted} inserted, {skipped} skipped")
    return inserted


async def run_full_pipeline(db: AsyncSession) -> dict:
    print("\n🚀 Starting SmartFlow ETL Pipeline...")
    results = {}

    print("\n[1/4] Processing LFA1 (Vendors)...")
    results["vendors"] = await load_table(db, transform_lfa1(extract("lfa1")), VendorDB, "LIFNR")

    print("\n[2/4] Processing MARA (Materials)...")
    results["materials"] = await load_table(db, transform_mara(extract("mara")), MaterialDB, "MATNR")

    print("\n[3/4] Processing EKKO (Purchase Orders)...")
    results["purchase_orders"] = await load_table(db, transform_ekko(extract("ekko")), PurchaseOrderDB, "EBELN")

    print("\n[4/4] Processing RBKP (Invoices)...")
    results["invoices"] = await load_table(db, transform_rbkp(extract("rbkp")), InvoiceDB, "BELNR")

    print("\n✅ ETL Pipeline completed successfully!")
    print(f"   Summary: {results}")
    return results


if __name__ == "__main__":
    import asyncio
    from backend.database import AsyncSessionLocal, create_tables

    async def test_pipeline():
        await create_tables()
        async with AsyncSessionLocal() as db:
            results = await run_full_pipeline(db)
            print(f"\n📊 Pipeline Results: {results}")

    asyncio.run(test_pipeline())