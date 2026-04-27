# dashboard/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="SmartFlow ERP Analytics",
    page_icon="📊",
    layout="wide"
)

API_BASE = "https://smartflow-l7u6.onrender.com/api"
# ── Helper: fetch data from API ───────────────────────────────
def fetch(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        return r.json()
    except:
        st.error(f"Could not connect to API at {API_BASE}")
        return None

# ── Header ────────────────────────────────────────────────────
st.title("📊 SmartFlow ERP Analytics Platform")
st.caption("Real-time procurement analytics powered by SAP data pipeline")
st.divider()

# ── Executive Summary Cards ───────────────────────────────────
summary = fetch("/analytics/summary")

if summary:
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        label="Total Vendors",
        value=summary["total_vendors"],
        delta=f"{summary['blocked_vendors']} blocked"
    )
    col2.metric(
        label="Total Materials",
        value=summary["total_materials"]
    )
    col3.metric(
        label="Purchase Orders",
        value=summary["total_pos"]
    )
    col4.metric(
        label="Total PO Spend",
        value=f"${summary['total_po_spend']:,.0f}"
    )
    col5.metric(
        label="Invoice Match Rate",
        value=f"{summary['invoice_match_rate']}%"
    )

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏢 Vendors", "📦 Purchase Orders", "🧾 Invoices"])


# ════════════════════════════════════════════════════════════
# TAB 1 — VENDORS
# ════════════════════════════════════════════════════════════
with tab1:
    vendor_data = fetch("/analytics/vendors")

    if vendor_data:
        col1, col2 = st.columns(2)

        # Vendor count by country — bar chart
        with col1:
            st.subheader("Vendors by Country")
            df_country = pd.DataFrame(vendor_data["by_country"])
            fig = px.bar(
                df_country,
                x="country", y="count",
                color="count",
                color_continuous_scale="Blues",
                labels={"country": "Country", "count": "Vendor Count"}
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # Top vendors by spend — horizontal bar
        with col2:
            st.subheader("Top 10 Vendors by Spend")
            df_top = pd.DataFrame(vendor_data["top_vendors"])
            fig2 = px.bar(
                df_top,
                x="total_spend", y="name",
                orientation="h",
                color="total_spend",
                color_continuous_scale="Greens",
                labels={"total_spend": "Total Spend ($)", "name": "Vendor"}
            )
            fig2.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Blocked vs Active vendors — donut
        st.subheader("Vendor Status")
        blocked = vendor_data["blocked_vendors"]
        active = vendor_data["total_vendors"] - blocked
        fig3 = go.Figure(data=[go.Pie(
            labels=["Active", "Blocked"],
            values=[active, blocked],
            hole=0.5,
            marker_colors=["#2ecc71", "#e74c3c"]
        )])
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)


# ════════════════════════════════════════════════════════════
# TAB 2 — PURCHASE ORDERS
# ════════════════════════════════════════════════════════════
with tab2:
    po_data = fetch("/analytics/purchase-orders")

    if po_data:
        col1, col2 = st.columns(2)

        # PO status breakdown — pie chart
        with col1:
            st.subheader("PO Status Breakdown")
            df_status = pd.DataFrame(po_data["by_status"])
            fig4 = px.pie(
                df_status,
                names="status", values="count",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig4, use_container_width=True)

        # Monthly PO trend — line chart
        with col2:
            st.subheader("Monthly PO Spend Trend")
            df_trend = pd.DataFrame(po_data["monthly_trend"])
            fig5 = px.line(
                df_trend,
                x="month", y="monthly_spend",
                markers=True,
                labels={"month": "Month", "monthly_spend": "Spend ($)"},
                color_discrete_sequence=["#3498db"]
            )
            st.plotly_chart(fig5, use_container_width=True)

        # Spend by currency — bar chart
        st.subheader("Spend by Currency")
        df_curr = pd.DataFrame(po_data["by_currency"])
        fig6 = px.bar(
            df_curr,
            x="currency", y="spend",
            color="currency",
            labels={"currency": "Currency", "spend": "Total Spend ($)"}
        )
        fig6.update_layout(showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)


# ════════════════════════════════════════════════════════════
# TAB 3 — INVOICES
# ════════════════════════════════════════════════════════════
with tab3:
    inv_data = fetch("/analytics/invoices")

    if inv_data:
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Invoices", inv_data["total_invoices"])
        col2.metric("Blocked Invoices",
                    inv_data["blocked_invoices"],
                    delta=f"{inv_data['blocked_pct']}% of total",
                    delta_color="inverse")
        col3.metric("Avg Tax Rate", f"{inv_data['avg_tax_rate']}%")

        st.divider()
        col1, col2 = st.columns(2)

        # Invoice status breakdown
        with col1:
            st.subheader("Invoice Status")
            df_inv_status = pd.DataFrame(inv_data["by_status"])
            fig7 = px.bar(
                df_inv_status,
                x="status", y="count",
                color="status",
                labels={"status": "Status", "count": "Count"}
            )
            fig7.update_layout(showlegend=False)
            st.plotly_chart(fig7, use_container_width=True)

        # Monthly invoice trend
        with col2:
            st.subheader("Monthly Invoice Trend")
            df_inv_trend = pd.DataFrame(inv_data["monthly_trend"])
            fig8 = px.area(
                df_inv_trend,
                x="month", y="monthly_amount",
                labels={"month": "Month", "monthly_amount": "Amount ($)"},
                color_discrete_sequence=["#9b59b6"]
            )
            st.plotly_chart(fig8, use_container_width=True)