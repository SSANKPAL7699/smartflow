# backend/main.py
# FastAPI application entry point — wires everything together

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import settings
from backend.database import create_tables, check_db_connection
from backend.services.sap_pipeline import run_full_pipeline
from backend.database import AsyncSessionLocal

from backend.routers import vendors, purchase_orders, invoices, analytics


# ── Startup & Shutdown ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    print(f"\n🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create DB tables
    await create_tables()

    # Run ETL pipeline on startup
    async with AsyncSessionLocal() as db:
        await run_full_pipeline(db)

    print("✅ SmartFlow API is ready!\n")
    yield
    print("👋 SmartFlow API shutting down...")


# ── App Instance ─────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## SmartFlow ERP Analytics Platform
    
    A FastAPI backend that simulates SAP data pipelines and exposes
    procurement analytics via REST API.
    
    ### SAP Tables Simulated
    - **LFA1** — Vendor Master
    - **MARA** — Material Master  
    - **EKKO** — Purchase Order Header
    - **RBKP** — Invoice Header
    
    ### Features
    - ETL pipeline runs on startup
    - KPI analytics endpoints
    - Filterable vendor/PO/invoice data
    """,
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
# Allows Streamlit dashboard to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────
app.include_router(vendors.router,          prefix=settings.API_PREFIX)
app.include_router(purchase_orders.router,  prefix=settings.API_PREFIX)
app.include_router(invoices.router,         prefix=settings.API_PREFIX)
app.include_router(analytics.router,        prefix=settings.API_PREFIX)


# ── Root Endpoints ───────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "app":     settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status":  "running",
        "docs":    "/docs",
    }

@app.get("/health")
async def health_check():
    db_status = await check_db_connection()
    return {
        "status":   "healthy",
        "database": db_status["status"],
        "version":  settings.APP_VERSION,
    }