import streamlit as st
import pandas as pd
import json
import os
import pydeck as pdk
from harvester import run_harvester, get_supabase_client, normalize_phone_number
from analytics_engine import calculate_lead_conversion_metrics, enrich_leads_with_analytics, export_leads_to_excel

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Cosmetics B2B/B2C Distribution Platform",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 6px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💄 Cosmetics B2B/B2C Distribution Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Lead Harvester, Geocoding, Phone Hygiene & Territory Analytics (AP & TS)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
st.sidebar.header("🎯 System Control Center")

pincode_input = st.sidebar.text_area(
    "📍 Target Locations or PIN Codes (AP & TS):",
    value="Khammam, Madhira, 500001, Vijayawada",
    help="Enter location names (e.g. Khammam, Madhira, Vijayawada, Vizag) or 6-digit PIN codes (e.g. 507001, 507203, 500001)."
)

segments_selected = st.sidebar.multiselect(
    "Target Business Segments:",
    options=["Commercial", "Institutional"],
    default=["Commercial", "Institutional"],
    help="Commercial: Salons, Spas, Kirana, Pharmacies. Institutional: Hostels, Colleges."
)

trigger_harvest = st.sidebar.button("🚀 Execute Lead Harvest", type="primary", use_container_width=True)

st.sidebar.divider()
st.sidebar.markdown("**🌐 Active Scraping Engines (9 Sources):**")
st.sidebar.caption("• Google Places (Place Details API)")
st.sidebar.caption("• Justdial SERP Directory")
st.sidebar.caption("• IndiaMART B2B Wholesalers")
st.sidebar.caption("• TradeIndia Regional Directory")
st.sidebar.caption("• Sulekha Beauty Parlours & Salons")
st.sidebar.caption("• AskLaila Regional Town Directory")
st.sidebar.caption("• Instagram & Facebook Bio Contacts")
st.sidebar.caption("• OpenStreetMap POI Geocoder")
st.sidebar.caption("• AP & TS Ground Truth Registry")

st.sidebar.divider()
st.sidebar.subheader("🔌 Database Connection")
supabase_client = get_supabase_client()
if supabase_client:
    st.sidebar.success("Supabase PostgreSQL Connected ✅")
else:
    st.sidebar.warning("Using Local Database Mode (JSON/CSV fallback)")

# Execute Harvester Trigger
if trigger_harvest:
    pincode_list = [p.strip() for p in pincode_input.split(",") if p.strip()]
    if pincode_list and segments_selected:
        with st.spinner("Harvesting business listings & verifying phone numbers..."):
            summary = run_harvester(pincode_list, segments_selected)
            st.session_state["latest_harvest"] = summary
            rec_count = len(summary.get("records", []))
            new_rec_count = summary.get("inserted_records", 0)
            st.toast(f"Harvest complete! {rec_count} verified listings ready ({new_rec_count} new added).", icon="🎉")

# -----------------------------------------------------------------------------
# Data Loader & Analytics Enrichment Function
# -----------------------------------------------------------------------------
@st.cache_data(ttl=10)
def load_leads_data() -> pd.DataFrame:

    supabase = get_supabase_client()
    raw_df = pd.DataFrame()
    if supabase:
        try:
            response = supabase.table("leads_master").select("*").order("created_at", desc=True).execute()
            if response.data:
                raw_df = pd.DataFrame(response.data)
        except Exception:
            pass
    
    if raw_df.empty:
        local_file = "leads_master_local.json"
        if os.path.exists(local_file):
            try:
                with open(local_file, "r") as f:
                    df = pd.DataFrame(json.load(f))
                    raw_df = df.iloc[::-1] if not df.empty else df
            except Exception:
                pass

    if raw_df.empty:
        raw_df = pd.DataFrame(columns=[
            "lead_id", "business_name", "segment", "state", "pincode", 
            "address_raw", "primary_phone", "phone_is_valid", "website", 
            "google_maps_url", "lead_status", "dedup_hash"
        ])

    return enrich_leads_with_analytics(raw_df)

df_leads = load_leads_data()

# -----------------------------------------------------------------------------
# Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📋 Lead Acquisition & Hygiene",
    "🗺️ Interactive Territory Map & Route Optimizer",
    "📈 Analytics & Lead Scoring Engine"
])

# -----------------------------------------------------------------------------
# TAB 1: Lead Acquisition & Data Hygiene
# -----------------------------------------------------------------------------
with tab1:
    if "latest_harvest" in st.session_state and st.session_state["latest_harvest"]:
        latest = st.session_state["latest_harvest"]
        df_latest = pd.DataFrame(latest.get("records", []))
        rec_len = len(df_latest)
        new_len = latest.get("inserted_records", 0)
        
        st.success(f"🎉 **Latest Harvest Results**: {rec_len} Verified Leads Harvested! ({new_len} new unique outlets added to database)")
        
        if not df_latest.empty:
            df_latest = enrich_leads_with_analytics(df_latest)
            cols_to_show = [c for c in ["business_name", "segment", "state", "pincode", "primary_phone", "phone_is_valid", "lead_score", "lead_grade", "estimated_monthly_order_inr", "address_raw", "website"] if c in df_latest.columns]
            st.dataframe(df_latest[cols_to_show], use_container_width=True, hide_index=True)
            
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                latest_csv = df_latest.to_csv(index=False).encode('utf-8')
                st.download_button(
                    f"📥 Download Latest Harvest CSV ({rec_len} Leads)",
                    data=latest_csv,
                    file_name=f"harvested_leads_{pincode_input.replace(' ', '_')}.csv",
                    mime="text/csv",
                    type="secondary"
                )
            with col_dl2:
                latest_excel = export_leads_to_excel(df_latest)
                st.download_button(
                    f"📊 Download Styled Excel (.xlsx) Report ({rec_len} Leads)",
                    data=latest_excel,
                    file_name=f"harvested_leads_{pincode_input.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            st.divider()

    col1, col2, col3, col4 = st.columns(4)
    total_leads = len(df_leads)
    if total_leads > 0:
        valid_phones = int(df_leads["phone_is_valid"].sum()) if "phone_is_valid" in df_leads.columns else 0
        phone_validity_pct = (valid_phones / total_leads) * 100
        unique_hashes = df_leads["dedup_hash"].nunique() if "dedup_hash" in df_leads.columns else total_leads
        duplicate_rate_pct = max(0.0, ((total_leads - unique_hashes) / total_leads) * 100)
        total_val = df_leads["estimated_monthly_order_inr"].sum() if "estimated_monthly_order_inr" in df_leads.columns else 0.0
    else:
        phone_validity_pct, duplicate_rate_pct, total_val = 0.0, 0.0, 0.0

    col1.metric("Total Lead Master Count", f"{total_leads:,}")
    col2.metric("Phone Hygiene Rate", f"{phone_validity_pct:.1f}%", delta="Target >90%")
    col3.metric("Duplicate Suppression", f"{duplicate_rate_pct:.2f}%", delta="Target <2.0%", delta_color="inverse")
    col4.metric("Pipeline Order Potential", f"₹{total_val:,.0f}")

    st.divider()

    st.subheader("📋 Master Leads Database Grid (with Quality Score & Order Potential)")
    if not df_leads.empty:
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        with filter_col1:
            state_filter = st.multiselect("Filter State:", df_leads["state"].unique().tolist(), default=df_leads["state"].unique().tolist())
        with filter_col2:
            pincode_options = ["All PIN Codes"] + sorted(df_leads["pincode"].astype(str).unique().tolist()) if "pincode" in df_leads.columns else ["All PIN Codes"]
            pincode_selected = st.selectbox("Filter PIN Code:", pincode_options, index=0)
        with filter_col3:
            segment_filter = st.multiselect("Filter Segment:", df_leads["segment"].unique().tolist(), default=df_leads["segment"].unique().tolist())
        with filter_col4:
            validity_filter = st.radio("Phone Hygiene:", ["All", "Valid Only", "Invalid Only"], horizontal=True)

        search_query = st.text_input("🔍 Search Business Name, Address, Location, or PIN Code:", value="", placeholder="Type location name (e.g. Khammam), PIN code (e.g. 507001), or business name...")

        df_filtered = df_leads.copy()
        if state_filter:
            df_filtered = df_filtered[df_filtered["state"].isin(state_filter)]
        if pincode_selected != "All PIN Codes" and "pincode" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["pincode"].astype(str) == str(pincode_selected)]
        if segment_filter:
            df_filtered = df_filtered[df_filtered["segment"].isin(segment_filter)]
        if validity_filter == "Valid Only":
            df_filtered = df_filtered[df_filtered["phone_is_valid"] == True]
        elif validity_filter == "Invalid Only":
            df_filtered = df_filtered[df_filtered["phone_is_valid"] == False]
        if search_query:
            q = search_query.lower().strip()
            df_filtered = df_filtered[
                df_filtered["business_name"].astype(str).str.lower().str.contains(q, na=False) |
                df_filtered["address_raw"].astype(str).str.lower().str.contains(q, na=False) |
                df_filtered["pincode"].astype(str).str.lower().str.contains(q, na=False) |
                df_filtered["state"].astype(str).str.lower().str.contains(q, na=False) |
                df_filtered["primary_phone"].astype(str).str.lower().str.contains(q, na=False)
            ]

        display_cols = ["business_name", "segment", "lead_score", "lead_grade", "estimated_monthly_order_inr", "state", "pincode", "primary_phone", "phone_is_valid", "address_raw", "website", "google_maps_url", "lead_status"]
        existing_display_cols = [c for c in display_cols if c in df_filtered.columns]

        st.dataframe(
            df_filtered[existing_display_cols],
            use_container_width=True,
            column_config={
                "business_name": st.column_config.TextColumn("Business Name", width="medium"),
                "lead_score": st.column_config.NumberColumn("Lead Score", format="%d/100", width="small"),
                "lead_grade": st.column_config.TextColumn("Grade", width="small"),
                "estimated_monthly_order_inr": st.column_config.NumberColumn("Est. Monthly Order (₹)", format="₹%d", width="small"),
                "primary_phone": st.column_config.TextColumn("Normalized Phone (+91)", width="small"),
                "phone_is_valid": st.column_config.CheckboxColumn("Valid Phone?", width="small"),
                "website": st.column_config.LinkColumn("Website", width="small"),
                "google_maps_url": st.column_config.LinkColumn("Google Maps Pin", width="medium")
            },
            hide_index=True
        )

        master_dl1, master_dl2 = st.columns(2)
        with master_dl1:
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Master CSV File", data=csv_data, file_name="cosmetics_leads_master.csv", mime="text/csv", use_container_width=True)
        with master_dl2:
            excel_data = export_leads_to_excel(df_filtered)
            st.download_button("📊 Export Master Excel (.xlsx) Workbook", data=excel_data, file_name="cosmetics_leads_master.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    else:
        st.info("No leads recorded yet. Click 'Execute Lead Harvest' in sidebar to acquire leads.")

# -----------------------------------------------------------------------------
# TAB 2: Interactive Territory Map & Route Optimizer
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("🗺️ Interactive Territory Map & Field Sales Route Optimizer")
    st.markdown("Color Legend: <span style='color:#EC4899;font-weight:bold;'>🌸 Salons & Spas</span> | <span style='color:#3B82F6;font-weight:bold;'>💊 Pharmacies</span> | <span style='color:#10B981;font-weight:bold;'>🏪 Kirana & Stores</span> | <span style='color:#8B5CF6;font-weight:bold;'>🏫 Colleges & Hostels</span>", unsafe_allow_html=True)
    
    if not df_leads.empty:
        df_map = df_leads.dropna(subset=["lat", "lon"]).copy()
        if not df_map.empty:
            def assign_marker_color(row):
                bname = str(row.get("business_name", "")).lower()
                seg = str(row.get("segment", ""))
                if seg == "Institutional":
                    return [139, 92, 246, 220]  # Purple
                elif any(k in bname for k in ["salon", "spa", "parlour", "makeover", "beauty"]):
                    return [236, 72, 153, 220]  # Pink
                elif any(k in bname for k in ["pharmacy", "medical", "medplus", "apollo"]):
                    return [59, 130, 246, 220]  # Blue
                else:
                    return [16, 185, 129, 220]  # Green

            df_map["color"] = df_map.apply(assign_marker_color, axis=1)

            avg_lat = df_map["lat"].mean()
            avg_lon = df_map["lon"].mean()

            scatterplot = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["lon", "lat"],
                get_fill_color="color",
                get_radius=180,
                radius_scale=2,
                radius_min_pixels=6,
                radius_max_pixels=25,
                pickable=True,
            )

            view_state = pdk.ViewState(
                latitude=avg_lat,
                longitude=avg_lon,
                zoom=11,
                pitch=20
            )

            st.pydeck_chart(pdk.Deck(
                layers=[scatterplot],
                initial_view_state=view_state,
                tooltip={
                    "html": "<b>{business_name}</b><br/>"
                            "<b>Segment:</b> {segment}<br/>"
                            "<b>PIN Code:</b> {pincode}<br/>"
                            "<b>Phone:</b> {primary_phone}<br/>"
                            "<b>Score:</b> {lead_score} ({lead_grade})<br/>"
                            "<b>Order Potential:</b> ₹{estimated_monthly_order_inr}",
                    "style": {"color": "white", "backgroundColor": "#1E293B", "fontSize": "13px"}
                }
            ))

            st.divider()
            st.markdown("##### 🚗 Field Sales Delivery Route Clusters")
            route_summary = df_map.groupby(["pincode", "state"]).agg(
                Outlets_Count=("business_name", "count"),
                Total_Order_Potential=("estimated_monthly_order_inr", "sum"),
                Avg_Lead_Score=("lead_score", "mean")
            ).reset_index()
            route_summary = route_summary.sort_values(by="Total_Order_Potential", ascending=False)
            
            st.dataframe(
                route_summary,
                use_container_width=True,
                column_config={
                    "pincode": st.column_config.TextColumn("Target PIN Code Route"),
                    "Outlets_Count": st.column_config.NumberColumn("Verified Outlets"),
                    "Total_Order_Potential": st.column_config.NumberColumn("Cluster Order Potential", format="₹%d"),
                    "Avg_Lead_Score": st.column_config.NumberColumn("Avg Route Score", format="%.1f/100")
                },
                hide_index=True
            )
        else:
            st.info("No geocoded lat/lon coordinates available for map rendering.")
    else:
        st.info("No leads available. Execute a lead harvest from the sidebar to populate the map.")

# -----------------------------------------------------------------------------
# TAB 3: Analytics & Lead Scoring Engine
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📈 Lead Lifecycle & Revenue Analytics")
    metrics = calculate_lead_conversion_metrics(df_leads)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Conversion Rate", f"{metrics['conversion_rate_pct']}%")
    m_col2.metric("Projected Wholesale Revenue", f"₹{metrics['projected_monthly_revenue_inr']:,.0f}")
    m_col3.metric("Total Pipeline Value", f"₹{metrics['total_pipeline_value_inr']:,.0f}")
    m_col4.metric("Avg Lead Score", f"{metrics['avg_lead_score']}/100")

    if not df_leads.empty:
        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            st.markdown("##### Leads by Quality Grade (A+ to C)")
            st.bar_chart(df_leads["lead_grade"].value_counts())
        with ch_col2:
            st.markdown("##### Leads by Segment (Commercial vs Institutional)")
            st.bar_chart(df_leads["segment"].value_counts())


