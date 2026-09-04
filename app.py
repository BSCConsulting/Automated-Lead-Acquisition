import streamlit as st
import pandas as pd
import json
import os
from harvester import run_harvester, get_supabase_client, normalize_phone_number
from analytics_engine import calculate_lead_conversion_metrics, approve_social_post
from social_agent import run_social_campaign_pipeline
from catalog_ingest import run_catalog_ingestion

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
    .post-card {
        background-color: #F8FAFC;
        border-left: 4px solid #EC4899;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💄 Cosmetics B2B/B2C Multi-Agent Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Lead Harvester, Multimodal Vision Catalog, Sales Webhook & Social Agent (AP & TS)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
st.sidebar.header("🎯 System Control Center")

pincode_input = st.sidebar.text_area(
    "Target Indian PIN Codes (AP & TS):",
    value="500001, 500081, 520001, 530001",
    help="Enter 6-digit PIN codes for Telangana (500-509) or Andhra Pradesh (515-535)."
)

segments_selected = st.sidebar.multiselect(
    "Target Business Segments:",
    options=["Commercial", "Institutional"],
    default=["Commercial", "Institutional"],
    help="Commercial: Salons, Spas, Kirana, Pharmacies. Institutional: Hostels, Colleges."
)

trigger_harvest = st.sidebar.button("🚀 Execute Lead Harvest", type="primary", use_container_width=True)

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
            st.toast(f"Harvest complete! {summary['inserted_records']} records processed.", icon="🎉")

# -----------------------------------------------------------------------------
# Data Loader Function
# -----------------------------------------------------------------------------
def load_leads_data() -> pd.DataFrame:
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table("leads_master").select("*").order("created_at", desc=True).execute()
            if response.data:
                return pd.DataFrame(response.data)
        except Exception:
            pass
    
    local_file = "leads_master_local.json"
    if os.path.exists(local_file):
        try:
            with open(local_file, "r") as f:
                df = pd.DataFrame(json.load(f))
                return df.iloc[::-1] if not df.empty else df
        except Exception:
            pass

    return pd.DataFrame(columns=[
        "lead_id", "business_name", "segment", "state", "pincode", 
        "address_raw", "primary_phone", "phone_is_valid", "website", 
        "google_maps_url", "lead_status", "dedup_hash"
    ])

df_leads = load_leads_data()

# -----------------------------------------------------------------------------
# Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Lead Acquisition & Hygiene",
    "📈 Analytics & Conversion Funnel",
    "📱 Social Agent Approval Queue",
    "🖼️ Vision Catalog Intelligence"
])

# -----------------------------------------------------------------------------
# TAB 1: Lead Acquisition & Data Hygiene
# -----------------------------------------------------------------------------
with tab1:
    # Render Latest Harvest Dedicated Banner if active
    if "latest_harvest" in st.session_state and st.session_state["latest_harvest"]:
        latest = st.session_state["latest_harvest"]
        st.success(f"🎉 **Latest Harvest Results**: {latest['inserted_records']} Leads Processed! (Duplicate Rate: {latest['duplicate_rate_pct']}%)")
        
        df_latest = pd.DataFrame(latest.get("records", []))
        if not df_latest.empty:
            cols_to_show = [c for c in ["business_name", "segment", "state", "pincode", "primary_phone", "phone_is_valid", "address_raw", "website"] if c in df_latest.columns]
            st.dataframe(df_latest[cols_to_show], use_container_width=True, hide_index=True)
            
            latest_csv = df_latest.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📥 Download Latest Harvest CSV ({latest['inserted_records']} Leads)",
                data=latest_csv,
                file_name=f"harvested_leads_{pincode_input.replace(' ', '_')}.csv",
                mime="text/csv",
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
        ap_count = len(df_leads[df_leads["state"] == "Andhra Pradesh"]) if "state" in df_leads.columns else 0
        ts_count = len(df_leads[df_leads["state"] == "Telangana"]) if "state" in df_leads.columns else 0
    else:
        phone_validity_pct, duplicate_rate_pct = 0.0, 0.0
        ap_count, ts_count = 0, 0

    col1.metric("Total Lead Master Count", f"{total_leads:,}")
    col2.metric("Phone Hygiene Rate", f"{phone_validity_pct:.1f}%", delta="Target >90%")
    col3.metric("Duplicate Suppression", f"{duplicate_rate_pct:.2f}%", delta="Target <2.0%", delta_color="inverse")
    col4.metric("Regional Split (TS / AP)", f"{ts_count} / {ap_count}")

    st.divider()

    st.subheader("📋 Master Leads Database Grid")
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

        search_query = st.text_input("🔍 Search Business Name or Address:", value="", placeholder="Type business name or keyword to search...")

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
            q = search_query.lower()
            df_filtered = df_filtered[
                df_filtered["business_name"].astype(str).str.lower().str.contains(q, na=False) |
                df_filtered["address_raw"].astype(str).str.lower().str.contains(q, na=False)
            ]

        display_cols = ["business_name", "segment", "state", "pincode", "primary_phone", "phone_is_valid", "address_raw", "website", "google_maps_url", "lead_status", "dedup_hash"]
        existing_display_cols = [c for c in display_cols if c in df_filtered.columns]

        st.dataframe(
            df_filtered[existing_display_cols],
            use_container_width=True,
            column_config={
                "business_name": st.column_config.TextColumn("Business Name", width="medium"),
                "primary_phone": st.column_config.TextColumn("Normalized Phone (+91)", width="small"),
                "phone_is_valid": st.column_config.CheckboxColumn("Valid Phone?", width="small"),
                "website": st.column_config.LinkColumn("Website", width="small"),
                "google_maps_url": st.column_config.LinkColumn("Google Maps Link", width="medium"),
                "dedup_hash": st.column_config.TextColumn("SHA-256 Hash", width="small")
            },
            hide_index=True
        )

        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Master Database CSV", data=csv_data, file_name="cosmetics_leads_master.csv", mime="text/csv")
    else:
        st.info("No leads recorded yet. Click 'Execute Lead Harvest' in sidebar to acquire leads.")

# -----------------------------------------------------------------------------
# TAB 2: Analytics & Conversion Funnel
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📈 Lead Lifecycle & Revenue Analytics")
    metrics = calculate_lead_conversion_metrics(df_leads)
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Conversion Rate", f"{metrics['conversion_rate_pct']}%")
    m_col2.metric("Projected Monthly Wholesale Revenue", f"₹{metrics['projected_monthly_revenue_inr']:,.2f}")
    m_col3.metric("Total Qualified Accounts", f"{metrics['total_leads']}")

    if not df_leads.empty:
        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            st.markdown("##### Leads by Segment")
            st.bar_chart(df_leads["segment"].value_counts())
        with ch_col2:
            st.markdown("##### Leads by State (AP vs TS)")
            st.bar_chart(df_leads["state"].value_counts())

# -----------------------------------------------------------------------------
# TAB 3: Social Agent Approval Queue
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📱 Social Media Campaign Pipeline (70% D2C / 30% B2B)")
    
    gen_col1, gen_col2 = st.columns([3, 1])
    with gen_col1:
        num_posts = st.number_input("Number of Posts to Generate:", min_value=1, max_value=20, value=5)
    with gen_col2:
        st.write("")
        st.write("")
        if st.button("✨ Generate Posts", type="primary"):
            with st.spinner("Generating bilingual posts via Gemini API..."):
                run_social_campaign_pipeline(total_posts=num_posts)
                st.success("Campaign pipeline updated!")

    # Display Pending Posts
    social_file = "social_posts_pending.json"
    if os.path.exists(social_file):
        with open(social_file, "r", encoding="utf-8") as f:
            posts = json.load(f)
        
        for idx, post in enumerate(posts):
            status_badge = "🟢 Approved" if post.get("status") == "Approved" else "🟡 Pending Approval"
            badge_color = "#10B981" if post.get("status") == "Approved" else "#F59E0B"
            
            with st.expander(f"Post #{idx+1} [{post.get('campaign_type')}] - {status_badge}", expanded=(idx==0)):
                st.markdown(f"**Campaign Type**: `{post.get('campaign_type')}` | **Status**: <span style='color:{badge_color};font-weight:bold;'>{post.get('status')}</span>", unsafe_allow_html=True)
                st.info(f"🎨 **Visual Asset Prompt**: {post.get('visual_asset_prompt')}")
                
                c_eng, c_tel = st.columns(2)
                with c_eng:
                    st.markdown("**English Caption:**")
                    st.text_area("EN", value=post.get("copy_english"), height=100, key=f"en_{idx}", disabled=True)
                with c_tel:
                    st.markdown("**Telugu Caption (తెలుగు):**")
                    st.text_area("TE", value=post.get("copy_telugu"), height=100, key=f"te_{idx}", disabled=True)

                if post.get("status") != "Approved":
                    if st.button(f"✅ Approve Post #{idx+1}", key=f"app_{idx}"):
                        approve_social_post(idx)
                        st.experimental_rerun()
    else:
        st.info("No social posts generated yet. Click 'Generate Posts' above.")

# -----------------------------------------------------------------------------
# TAB 4: Vision Catalog Intelligence
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("🖼️ CatalogGenius Multimodal Ingestion")
    if st.button("🔍 Run Catalog OCR Extraction"):
        with st.spinner("Extracting MRP & Wholesale Pricing from raw supplier images..."):
            run_catalog_ingestion()
            st.success("Catalog extraction completed!")

    cat_file = "catalog_output.csv"
    if os.path.exists(cat_file):
        df_cat = pd.read_csv(cat_file)
        st.dataframe(df_cat, use_container_width=True)
    else:
        st.info("No catalog extraction file found. Click 'Run Catalog OCR Extraction' above.")
