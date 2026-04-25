# backend/services/analytics.py
# KPI calculations for the SmartFlow dashboard
# Queries the database and returns analytics metrics

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


# ══════════════════════════════════════════════════════════════
# VENDOR ANALYTICS (LFA1 + EKKO)
# ══════════════════════════════════════════════════════════════
async def get_vendor_analytics(db: AsyncSession) -> dict:
    """
    Returns vendor KPIs:
    - Total vendors, blocked vendors
    - Top vendors by spend
    - Vendor count by country
    """
    # Total & blocked vendors
    result = await db.execute(text("""
        SELECT 
            COUNT(*) as total_vendors,
            SUM(CASE WHEN LIFSP = 'X' THEN 1 ELSE 0 END) as blocked_vendors
        FROM lfa1_vendors
    """))
    row = result.fetchone()
    total_vendors   = row[0]
    blocked_vendors = row[1]

    # Top 10 vendors by total PO spend
    result = await db.execute(text("""
        SELECT 
            v.LIFNR,
            v.NAME1,
            v.LAND1,
            COUNT(p.EBELN)      as po_count,
            SUM(p.NETWR)        as total_spend
        FROM lfa1_vendors v
        LEFT JOIN ekko_purchase_orders p ON v.LIFNR = p.LIFNR
        GROUP BY v.LIFNR, v.NAME1, v.LAND1
        ORDER BY total_spend DESC
        LIMIT 10
    """))
    top_vendors = [
        {
            "vendor_id":   r[0],
            "name":        r[1],
            "country":     r[2],
            "po_count":    r[3],
            "total_spend": round(r[4] or 0, 2),
        }
        for r in result.fetchall()
    ]

    # Vendor count by country
    result = await db.execute(text("""
        SELECT LAND1, COUNT(*) as vendor_count
        FROM lfa1_vendors
        GROUP BY LAND1
        ORDER BY vendor_count DESC
    """))
    by_country = [
        {"country": r[0], "count": r[1]}
        for r in result.fetchall()
    ]

    return {
        "total_vendors":   total_vendors,
        "blocked_vendors": blocked_vendors,
        "blocked_pct":     round((blocked_vendors / total_vendors) * 100, 1),
        "top_vendors":     top_vendors,
        "by_country":      by_country,
    }


# ══════════════════════════════════════════════════════════════
# PURCHASE ORDER ANALYTICS (EKKO)
# ══════════════════════════════════════════════════════════════
async def get_po_analytics(db: AsyncSession) -> dict:
    """
    Returns PO KPIs:
    - Total POs, total spend
    - PO status breakdown
    - Monthly PO trend
    - Spend by currency
    """
    # Total POs and spend
    result = await db.execute(text("""
        SELECT 
            COUNT(*)        as total_pos,
            SUM(NETWR)      as total_spend,
            AVG(NETWR)      as avg_po_value
        FROM ekko_purchase_orders
    """))
    row = result.fetchone()
    total_pos   = row[0]
    total_spend = round(row[1] or 0, 2)
    avg_value   = round(row[2] or 0, 2)

    # PO status breakdown
    result = await db.execute(text("""
        SELECT STATUS, COUNT(*) as count, SUM(NETWR) as spend
        FROM ekko_purchase_orders
        GROUP BY STATUS
        ORDER BY count DESC
    """))
    by_status = [
        {
            "status": r[0],
            "count":  r[1],
            "spend":  round(r[2] or 0, 2)
        }
        for r in result.fetchall()
    ]

    # Monthly PO trend (count + spend by month)
    result = await db.execute(text("""
        SELECT 
            SUBSTR(BEDAT, 1, 7)  as month,
            COUNT(*)             as po_count,
            SUM(NETWR)           as monthly_spend
        FROM ekko_purchase_orders
        WHERE BEDAT IS NOT NULL
        GROUP BY month
        ORDER BY month
    """))
    monthly_trend = [
        {
            "month":         r[0],
            "po_count":      r[1],
            "monthly_spend": round(r[2] or 0, 2)
        }
        for r in result.fetchall()
    ]

    # Spend by currency
    result = await db.execute(text("""
        SELECT WAERS, COUNT(*) as count, SUM(NETWR) as spend
        FROM ekko_purchase_orders
        GROUP BY WAERS
        ORDER BY spend DESC
    """))
    by_currency = [
        {
            "currency": r[0],
            "count":    r[1],
            "spend":    round(r[2] or 0, 2)
        }
        for r in result.fetchall()
    ]

    return {
        "total_pos":     total_pos,
        "total_spend":   total_spend,
        "avg_po_value":  avg_value,
        "by_status":     by_status,
        "monthly_trend": monthly_trend,
        "by_currency":   by_currency,
    }


# ══════════════════════════════════════════════════════════════
# INVOICE ANALYTICS (RBKP)
# ══════════════════════════════════════════════════════════════
async def get_invoice_analytics(db: AsyncSession) -> dict:
    """
    Returns Invoice KPIs:
    - Total invoices, total amount
    - Payment blocked invoices
    - Invoice status breakdown
    - Average tax rate
    """
    # Totals
    result = await db.execute(text("""
        SELECT 
            COUNT(*)        as total_invoices,
            SUM(RMWWR)      as total_gross,
            SUM(WMWST)      as total_tax,
            SUM(NETWR)      as total_net,
            SUM(CASE WHEN ZLSPR = 'A' THEN 1 ELSE 0 END) as blocked_invoices
        FROM rbkp_invoices
    """))
    row = result.fetchone()
    total_invoices   = row[0]
    total_gross      = round(row[1] or 0, 2)
    total_tax        = round(row[2] or 0, 2)
    total_net        = round(row[3] or 0, 2)
    blocked_invoices = row[4]
    avg_tax_rate     = round((total_tax / total_gross * 100), 2) if total_gross else 0

    # Invoice status breakdown
    result = await db.execute(text("""
        SELECT RBSTAT, COUNT(*) as count, SUM(RMWWR) as amount
        FROM rbkp_invoices
        GROUP BY RBSTAT
        ORDER BY count DESC
    """))
    by_status = [
        {
            "status": r[0],
            "count":  r[1],
            "amount": round(r[2] or 0, 2)
        }
        for r in result.fetchall()
    ]

    # Monthly invoice trend
    result = await db.execute(text("""
        SELECT 
            SUBSTR(BLDAT, 1, 7) as month,
            COUNT(*)            as invoice_count,
            SUM(RMWWR)          as monthly_amount
        FROM rbkp_invoices
        WHERE BLDAT IS NOT NULL
        GROUP BY month
        ORDER BY month
    """))
    monthly_trend = [
        {
            "month":          r[0],
            "invoice_count":  r[1],
            "monthly_amount": round(r[2] or 0, 2)
        }
        for r in result.fetchall()
    ]

    return {
        "total_invoices":   total_invoices,
        "total_gross":      total_gross,
        "total_tax":        total_tax,
        "total_net":        total_net,
        "blocked_invoices": blocked_invoices,
        "blocked_pct":      round((blocked_invoices / total_invoices) * 100, 1),
        "avg_tax_rate":     avg_tax_rate,
        "by_status":        by_status,
        "monthly_trend":    monthly_trend,
    }


# ══════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY — All KPIs in one call
# ══════════════════════════════════════════════════════════════
async def get_executive_summary(db: AsyncSession) -> dict:
    """
    Single endpoint for dashboard header KPIs.
    Combines vendor + PO + invoice metrics.
    """
    result = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM lfa1_vendors)              as total_vendors,
            (SELECT COUNT(*) FROM mara_materials)            as total_materials,
            (SELECT COUNT(*) FROM ekko_purchase_orders)      as total_pos,
            (SELECT SUM(NETWR) FROM ekko_purchase_orders)    as total_po_spend,
            (SELECT COUNT(*) FROM rbkp_invoices)             as total_invoices,
            (SELECT SUM(RMWWR) FROM rbkp_invoices)           as total_invoice_amt,
            (SELECT COUNT(*) FROM rbkp_invoices 
             WHERE ZLSPR = 'A')                              as blocked_invoices,
            (SELECT COUNT(*) FROM lfa1_vendors 
             WHERE LIFSP = 'X')                              as blocked_vendors
    """))
    row = result.fetchone()

    total_po_spend      = row[3] or 0
    total_invoice_amt   = row[5] or 0
    invoice_match_rate  = round((total_invoice_amt / total_po_spend * 100), 1) if total_po_spend else 0

    return {
        "total_vendors":      row[0],
        "total_materials":    row[1],
        "total_pos":          row[2],
        "total_po_spend":     round(total_po_spend, 2),
        "total_invoices":     row[4],
        "total_invoice_amt":  round(total_invoice_amt, 2),
        "blocked_invoices":   row[6],
        "blocked_vendors":    row[7],
        "invoice_match_rate": invoice_match_rate,
    }


# ══════════════════════════════════════════════════════════════
# Quick test when run directly
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import asyncio
    from backend.database import AsyncSessionLocal

    async def test():
        async with AsyncSessionLocal() as db:
            print("\n📊 Executive Summary:")
            summary = await get_executive_summary(db)
            for k, v in summary.items():
                print(f"  {k:25s}: {v}")

            print("\n📊 PO Analytics:")
            po = await get_po_analytics(db)
            print(f"  Total POs    : {po['total_pos']}")
            print(f"  Total Spend  : {po['total_spend']:,.2f}")
            print(f"  Avg PO Value : {po['avg_po_value']:,.2f}")
            print(f"  By Status    : {po['by_status']}")

            print("\n📊 Invoice Analytics:")
            inv = await get_invoice_analytics(db)
            print(f"  Total Invoices  : {inv['total_invoices']}")
            print(f"  Blocked         : {inv['blocked_invoices']} ({inv['blocked_pct']}%)")
            print(f"  Avg Tax Rate    : {inv['avg_tax_rate']}%")

    asyncio.run(test())