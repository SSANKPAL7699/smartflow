# 📊 SmartFlow ERP Analytics Platform

A full-stack data engineering project that simulates SAP procurement data pipelines and exposes real-time KPI analytics through a REST API and interactive dashboard.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12 |
| Database | SQLAlchemy (async), SQLite |
| ETL Pipeline | Pandas, custom SAP simulator |
| Dashboard | Streamlit, Plotly |
| Testing | pytest, pytest-asyncio, httpx |
| Containerization | Docker, Docker Compose |

---

## 🏗️ Architecture
SAP Data Simulation (CSV)
↓
ETL Pipeline (Pandas)
↓
SQLite Database
↓
FastAPI REST API (12 endpoints)
↓
Streamlit Dashboard (Plotly charts)
---

## 📁 Project Structure
smartflow/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # App settings
│   ├── database.py          # Async DB engine
│   ├── models/              # SQLAlchemy + Pydantic models
│   │   ├── vendor.py
│   │   ├── material.py
│   │   ├── purchase_order.py
│   │   └── invoice.py
│   ├── routers/             # API route handlers
│   │   ├── vendors.py
│   │   ├── purchase_orders.py
│   │   ├── invoices.py
│   │   └── analytics.py
│   └── services/
│       ├── sap_pipeline.py  # ETL pipeline
│       └── analytics.py     # KPI calculations
├── dashboard/
│   └── app.py               # Streamlit dashboard
├── data/simulated/          # Generated SAP data (CSV)
├── tests/
│   └── test_api.py          # API tests (7 tests, all passing)
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.dashboard
├── docker-compose.yml
└── requirements.txt
---

## 📊 SAP Tables Simulated

| SAP Table | Description | Records |
|-----------|-------------|---------|
| LFA1 | Vendor Master | 50 |
| MARA | Material Master | 100 |
| EKKO | Purchase Order Header | 200 |
| RBKP | Invoice Header | 180 |

---

## 📈 Key KPIs

- **Total PO Spend:** $49.3M
- **Invoice Match Rate:** 89.6%
- **Blocked Invoices:** 21.7%
- **Avg Tax Rate:** 12.6%

---

## 🛠️ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/smartflow.git
cd smartflow
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the backend
```bash
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run the dashboard (new terminal)
```bash
streamlit run dashboard/app.py
```

### 5. Run with Docker
```bash
docker-compose up --build
```

---

## 🧪 Running Tests

```bash
python3 -m pytest tests/ -v
```
---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vendors/ | List all vendors |
| GET | /api/vendors/{id} | Get vendor by ID |
| GET | /api/vendors/stats/summary | Vendor statistics |
| GET | /api/purchase-orders/ | List all POs |
| GET | /api/purchase-orders/{id} | Get PO by ID |
| GET | /api/invoices/ | List all invoices |
| GET | /api/invoices/{id} | Get invoice by ID |
| GET | /api/analytics/summary | Executive KPI summary |
| GET | /api/analytics/vendors | Vendor analytics |
| GET | /api/analytics/purchase-orders | PO analytics |
| GET | /api/analytics/invoices | Invoice analytics |
| GET | /docs | Swagger UI |

---

## 👩‍💻 Author

**Shreya Sankpal**
MS Computer Science — SUNY Binghamton (Dec 2026)
3 years SAP ABAP experience
Targeting: Backend SWE | Data Engineering | Cloud/DevOps