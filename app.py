"""
AI-Powered Intelligent Assistant for Indian Standards and BIS Services
Department of Consumer Affairs (DoCA), Ministry of Consumer Affairs, Food & Public Distribution
Smart Automation | Problem Statement ID: 26107
"""

import os
import csv
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load .env variables
load_dotenv(override=True)

from search_loop import BISSearchLoop
from scraper import BISScraper, save_to_csv
from bis_knowledge import BIS_SCHEMES, BIS_LABORATORIES, CONSUMER_SERVICES

# Streamlit Page Config
st.set_page_config(
    page_title="BIS AI Assistant | Indian Standards & Services",
    page_icon="BIS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* Hide Deploy button and header decorations */
    .stAppDeployButton, 
    [data-testid="stAppDeployButton"], 
    [data-testid="stToolbar"] [data-testid="stAppDeployButton"],
    #stDecoration {
        display: none !important;
        visibility: hidden !important;
    }

    /* Decrease upper padding of the page container */
    .block-container, 
    [data-testid="stMainBlockContainer"],
    div.stMainBlockContainer {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Compact header */
    header[data-testid="stHeader"] {
        height: 1.5rem !important;
        background-color: transparent !important;
    }
    
    /* Sticky Navigation Navbar (Tabs remain fixed when scrolling) */
    div[data-testid="stTabs"] > div[role="tablist"] {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background: #ffffff !important;
        padding: 0.6rem 0.5rem !important;
        border-bottom: 2px solid #005ead !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08) !important;
        border-radius: 6px 6px 0 0 !important;
    }
    
    /* Tab buttons typography */
    div[data-testid="stTabs"] button[role="tab"] {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1rem !important;
        color: #334155 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #005ead !important;
        border-bottom: 3px solid #005ead !important;
    }

    .main-header {
        background: linear-gradient(135deg, #0b3c5d 0%, #1d2731 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #f9ba32;
        margin: 0;
        font-size: 1.8rem;
    }
    .main-header p {
        color: #e0e0e0;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }
    .tag-pill {
        display: inline-block;
        background-color: #e8f4fd;
        color: #005ead;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.3rem;
    }
    .loop-badge {
        display: inline-block;
        background-color: #e6f4ea;
        color: #137333;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        border: 1px solid #ceead6;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "standards_data.csv"

@st.cache_resource
def get_search_loop():
    return BISSearchLoop(CSV_FILE)

search_loop = get_search_loop()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px 6px; margin-bottom: 14px; background: linear-gradient(180deg, #f0f7fc 0%, #ffffff 100%); border-radius: 10px; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
        <svg width="64" height="64" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="48" fill="#0b3c5d" stroke="#f9ba32" stroke-width="3"/>
            <circle cx="50" cy="50" r="39" fill="#ffffff"/>
            <!-- BIS Standard Diamond / Cog Emblem -->
            <polygon points="50,20 66,35 66,56 50,71 34,56 34,35" fill="#005ead" stroke="#0b3c5d" stroke-width="1.5"/>
            <circle cx="50" cy="46" r="10" fill="#f9ba32" stroke="#0b3c5d" stroke-width="1.5"/>
            <text x="50" y="50" font-size="9" font-weight="900" fill="#0b3c5d" text-anchor="middle" font-family="Arial, sans-serif">मानक:</text>
            <text x="50" y="83" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle" font-family="Arial, sans-serif">BIS • INDIA</text>
        </svg>
        <div style="text-align: center; margin-top: 8px;">
            <span style="font-weight: 800; font-size: 1.05rem; color: #0b3c5d; display: block; letter-spacing: 0.5px;">भारतीय मानक ब्यूरो</span>
            <span style="font-size: 0.75rem; font-weight: 700; color: #005ead; display: block;">BUREAU OF INDIAN STANDARDS</span>
            <span style="font-size: 0.7rem; color: #64748b; display: block; margin-top: 2px;">Govt. of India | DoCA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### **DoCA & BIS Portal**")
    st.caption("Ministry of Consumer Affairs, Food & Public Distribution")
    
    st.divider()
    st.subheader("System & Model Settings")
    
    language = st.selectbox(
        "Response Language",
        ["English", "हिन्दी (Hindi)", "Hinglish"],
        index=0
    )
    
    provider_choice = st.selectbox(
        "LLM Engine",
        ["Auto / Fallback Engine", "Google Gemini", "Groq (Llama 3.3)", "OpenAI (GPT-4o)"],
        index=0
    )
    
    # Check .env status
    gemini_env = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    groq_env = bool(os.environ.get("GROQ_API_KEY"))
    openai_env = bool(os.environ.get("OPENAI_API_KEY"))

    st.markdown("**.env API Key Status:**")
    st.markdown(f"- **Gemini Key**: {'Configured in .env' if gemini_env else 'Not Configured'}")
    st.markdown(f"- **Groq Key**: {'Configured in .env' if groq_env else 'Not Configured'}")
    st.markdown(f"- **OpenAI Key**: {'Configured in .env' if openai_env else 'Not Configured'}")
    st.caption("Keys can be placed in `.env` or supplied below for this session.")

    custom_api_key = None
    if provider_choice != "Auto / Fallback Engine":
        custom_api_key = st.text_input(
            f"Override {provider_choice} Key (Optional):",
            type="password",
            help="Overrides the key in .env for this session."
        )

    st.divider()
    st.subheader("Automated Search & Scrape Settings")
    live_scrape_enabled = st.toggle("Live Web Scrape on Every Query", value=True, help="When enabled, queries standardsbis.bsbedge.com live, scrapes matching standards, updates standards_data.csv, and runs LLM 1 & LLM 2.")
    max_scrape_per_query = st.slider("Max items to scrape per query", min_value=1, max_value=15, value=5)

    st.divider()
    st.subheader("Knowledge Base Statistics")
    if os.path.exists(CSV_FILE):
        try:
            df_stat = pd.read_csv(CSV_FILE)
            st.metric("Standards in CSV Database", len(df_stat))
            active_count = len(df_stat[df_stat['status'].str.lower() == 'active'])
            st.metric("Active Standards", active_count)
        except Exception:
            st.write("Reading database...")
    else:
        st.warning("CSV Database not initialized.")

    st.divider()
    st.subheader("Official Portals")
    st.markdown("""
    - [e-Sale Portal (standardsbis.bsbedge.com)](https://standardsbis.bsbedge.com)
    - [Manakonline (e-BIS)](https://www.manakonline.in)
    - [CRS Portal (crsbis.in)](https://www.crsbis.in)
    - [National Consumer Helpline](https://consumerhelpline.gov.in)
    """)

# ----------------- MAIN HEADER -----------------
st.markdown("""
<div class="main-header">
    <span class="tag-pill">SIH Problem Statement 26107</span>
    <span class="tag-pill">Smart Automation</span>
    <span class="tag-pill">DoCA / BIS</span>
    <span class="tag-pill">Continuous Search Loop</span>
    <h1>AI-Powered Intelligent Assistant for Indian Standards & BIS Services</h1>
    <p>Automated Loop: Search Webpage ➔ Scrape Data & HTML Preview ➔ Store in CSV ➔ LLM 1 Filter ➔ LLM 2 Advisory Response.</p>
</div>
""", unsafe_allow_html=True)

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Conversational Assistant (Live Search & Dual-LLM Loop)",
    "Manual Web Scraper",
    "Standards CSV Database",
    "BIS Schemes & Hallmarking Guide"
])

# Initialize session state for loop query
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------- TAB 1: CONVERSATIONAL ASSISTANT -----------------
with tab1:
    col_chat, col_inspect = st.columns([1.15, 0.85])

    with col_chat:
        st.subheader("Interactive BIS Query Loop")
        st.caption("Every query searches standardsbis.bsbedge.com, scrapes all webpage data, saves to CSV, and processes through LLM 1 & LLM 2.")

        # Quick Inquiries (3 compact buttons in one row)
        st.markdown("**Quick Inquiries (Click to run):**")
        sample_queries = [
            ("IS 10500: Drinking Water", "IS 10500 drinking water specifications"),
            ("IS 694: PVC Cables (ISI Mark)", "How can an MSME get an ISI mark for PVC cables?"),
            ("IS 1417: Gold Hallmarking & HUID", "What is 6-digit HUID and how to verify gold hallmarking?")
        ]

        cols_btn = st.columns(3)
        clicked_query = None
        for i, (label, query_text) in enumerate(sample_queries):
            if cols_btn[i].button(label, key=f"quick_btn_{i}", use_container_width=True):
                clicked_query = query_text
                st.session_state["user_query_input"] = query_text

        # User Query Input
        user_query = st.text_input(
            "Enter Keyword, Product, or IS Number:",
            value=clicked_query if clicked_query else st.session_state.get("user_query_input", ""),
            placeholder="e.g., IS 10500, IS 138, pressure cooker, battery charger, solar inverter...",
            key="user_query_input"
        )

        submit_btn = st.button("Search and Analyze", type="primary", use_container_width=True)

    with col_inspect:
        st.subheader("Automated Loop & Pipeline Inspector")
        st.caption("Live tracking of each step in the workflow loop:")
        st.info("Webpage Search ➔ Scrape Data & HTML Doc ➔ Store in CSV ➔ LLM 1 (Filter) ➔ LLM 2 (Advisor)")

    # Determine query to execute (either from quick click or text submission)
    query_to_run = clicked_query or (user_query.strip() if submit_btn and user_query.strip() else None)

    if query_to_run:
        with st.spinner(f"Executing Automated Search, Scrape, and Dual-LLM Loop for '{query_to_run}'..."):
            # Map provider
            prov_map = {
                "Auto / Fallback Engine": "auto",
                "Google Gemini": "gemini",
                "Groq (Llama 3.3)": "groq",
                "OpenAI (GPT-4o)": "openai"
            }
            chosen_prov = prov_map.get(provider_choice, "auto")

            # Execute full loop pass
            result = search_loop.execute_loop_iteration(
                user_query=query_to_run,
                language="Hindi" if "Hindi" in language else "English",
                provider=chosen_prov,
                custom_key=custom_api_key,
                max_scrape_items=max_scrape_per_query,
                enable_live_scrape=live_scrape_enabled
            )

            # Record in session chat history
            st.session_state.chat_history.insert(0, result)

    # Display Current / Latest Result
    if st.session_state.chat_history:
        latest = st.session_state.chat_history[0]
        
        with col_chat:
            st.markdown(f"""
            <div class="loop-badge">
                <b>Execution Complete for:</b> "{latest['user_query']}" | 
                <b>Scraped from Web:</b> {latest['scraped_count']} | 
                <b>Saved to CSV:</b> +{latest['newly_saved_count']} | 
                <b>Engine:</b> {latest['provider_used']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown(latest["llm2_output"])

        with col_inspect:
            st.markdown("### Loop Step Execution Details")
            
            with st.expander("Step 1 & 2: Live Web Search & Scraped Records", expanded=True):
                search_mode = "Specific IS Number Search" if latest.get("is_standard_number") else "Product / Keyword Search"
                st.markdown(f"- **Search Mode**: `{search_mode}`")
                st.markdown(f"- **Search Query**: `{latest['search_term']}`")
                st.markdown(f"- **Target URL**: [{latest.get('target_url')}]({latest.get('target_url')})")
                st.markdown(f"- **Total Standards Scraped from Webpage**: `{latest['scraped_count']}`")
                st.markdown(f"- **New Records Added to CSV**: `+{latest['newly_saved_count']}`")
                if latest.get("scraped_items"):
                    st.write("**Scraped Items from Webpage:**")
                    for item in latest["scraped_items"][:4]:
                        st.markdown(f"- **`{item.get('is_no')}`**: {item.get('title')} `[{item.get('status')}]` (Price: {item.get('price_in_india')})")

            with st.expander("Step 3: Candidate Standards Matched from CSV", expanded=False):
                st.write(f"**Found {len(latest['scored_candidates'])} candidate match(es):**")
                for std, sc in latest["scored_candidates"]:
                    st.markdown(f"- **`{std.get('is_no')}`** (Score: {sc:.1f}): {std.get('title')} `[{std.get('status')}]`")
                st.text_area("Candidates Formatted for LLM 1", latest["candidates_text"], height=160)

            with st.expander("Step 4: LLM 1 (Technical Extractor & Candidate Filter)", expanded=True):
                st.markdown(f"**Model Provider**: `{latest['provider_used']}`")
                st.markdown(latest["llm1_output"])

            with st.expander("Step 5: LLM 2 Synthesizer Input & Prompt Info", expanded=False):
                st.text(f"Language: {latest['language']}\nQuery: {latest['user_query']}\nPrompt contains LLM 1 structured findings + BIS Scheme rules.")


# ----------------- TAB 2: MANUAL WEB SCRAPER -----------------
with tab2:
    st.subheader("Dedicated Web Scraper for standardsbis.bsbedge.com")
    st.markdown("""
    Use this tool to bulk-scrape standards for any category or keyword directly from the **BIS e-Sale Portal**:
    - **Extracts**: IS Number, Title, Status, Technical Committee, Amendments, Prices.
    - **Rule Preview**: Automatically fetches the HTML preview from `BIS_Preview.aspx?id=...` for Scope & Foreword.
    - **Saves to**: `standards_data.csv`.
    """)

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        scrape_keyword = st.text_input("Enter keyword to scrape:", value="fire extinguisher", placeholder="e.g., pressure cooker, battery, medical device...")
    with col_s2:
        max_scrape = st.number_input("Max items to fetch:", min_value=1, max_value=20, value=6)

    if st.button("Scrape Standards to Database", type="primary"):
        with st.spinner(f"Scraping standardsbis.bsbedge.com for '{scrape_keyword}'..."):
            clean_term, is_std = search_loop.extract_search_keyword(scrape_keyword)
            items = search_loop.scraper.scrape_and_enrich(
                clean_term,
                is_standard_number=is_std,
                fetch_descriptions=True,
                max_items=max_scrape
            )
            if items:
                added = save_to_csv(items, CSV_FILE, append=True)
                search_loop.retriever.load_data()  # refresh retriever cache
                st.success(f"Successfully scraped {len(items)} items ({'IS Number Search' if is_std else 'Keyword Search'})! Added {added} new unique standard(s) to '{CSV_FILE}'.")
                
                df_scraped = pd.DataFrame(items)
                st.dataframe(df_scraped[["is_no", "title", "status", "technical_committee", "price_in_india", "price_outside_india", "preview_id"]], use_container_width=True)
            else:
                st.warning("No standards found on the live portal for this keyword, or server connection timed out.")


# ----------------- TAB 3: STANDARDS CSV EXPLORER -----------------
with tab3:
    st.subheader("Standards Knowledge Base Explorer")
    st.caption(f"Browsing `{CSV_FILE}` (dynamically updated by every search-and-scrape cycle).")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        
        # Search & Filter
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            filter_text = st.text_input("Filter database by title, IS number, or committee:", "")
        with col_f2:
            status_filter = st.selectbox("Status Filter", ["All", "Active", "Withdrawn"])

        filtered_df = df.copy()
        if filter_text:
            mask = (
                filtered_df["is_no"].astype(str).str.contains(filter_text, case=False, na=False) |
                filtered_df["title"].astype(str).str.contains(filter_text, case=False, na=False) |
                filtered_df["technical_committee"].astype(str).str.contains(filter_text, case=False, na=False) |
                filtered_df["description"].astype(str).str.contains(filter_text, case=False, na=False)
            )
            filtered_df = filtered_df[mask]

        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["status"].str.lower() == status_filter.lower()]

        st.write(f"Displaying **{len(filtered_df)}** of **{len(df)}** standards in CSV:")
        st.dataframe(
            filtered_df[["is_no", "title", "status", "technical_committee", "amendments", "price_in_india", "price_outside_india"]],
            use_container_width=True
        )

        # Standard Detail Inspector
        if not filtered_df.empty:
            st.markdown("### Standard Scope and National Foreword Inspector")
            selected_is = st.selectbox("Select Standard to view preview document & scope:", filtered_df["is_no"].tolist())
            row = filtered_df[filtered_df["is_no"] == selected_is].iloc[0]
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", row.get("status", "Active"))
            c2.metric("Committee", row.get("technical_committee", "N/A"))
            c3.metric("Price (India)", row.get("price_in_india", "N/A"))
            c4.metric("Amendments", str(row.get("amendments", "0")))

            st.markdown(f"**Full Title**: {row.get('title')}")
            st.markdown(f"**Reaffirmed Year**: {row.get('reaffirmed_year') or 'Current'}")
            
            st.markdown("**Rule Description / Scope (from HTML Preview Doc):**")
            st.info(row.get("description") or "No description preview available.")
            
            if row.get("preview_url"):
                st.markdown(f"[Open Official BIS Preview Document]({row.get('preview_url')})")

        # CSV Download Button
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download standards_data.csv",
            data=csv_bytes,
            file_name="standards_data.csv",
            mime="text/csv",
            type="secondary"
        )
    else:
        st.error("CSV file not found.")


# ----------------- TAB 4: SCHEMES & HALLMARKING GUIDE -----------------
with tab4:
    st.subheader("Comprehensive Guide to BIS Schemes & Conformity Assessment")
    
    st.markdown("### 1. BIS Certification Schemes Overview")
    for s_title, s_info in BIS_SCHEMES.items():
        with st.expander(f"{s_title}", expanded=False):
            st.markdown(f"**Type**: `{s_info.get('type')}`")
            st.markdown(f"**Application Portal**: `{s_info.get('portal')}`")
            st.markdown(f"**Summary**: {s_info.get('description')}")
            if "applicable_sectors" in s_info:
                st.markdown("**Core Products Covered:**")
                for sec in s_info["applicable_sectors"]:
                    st.markdown(f"- {sec}")
            if "licensing_steps" in s_info:
                st.markdown("**Licensing Process Roadmap:**")
                for stp in s_info["licensing_steps"]:
                    st.markdown(f"  - {stp}")
            if "msme_concessions" in s_info:
                st.info(f"**MSME & Startup Benefits**: {s_info['msme_concessions']}")

    st.divider()
    st.markdown("### 2. Gold & Silver Hallmarking (HUID Guide)")
    h_info = BIS_SCHEMES["Hallmarking Scheme (Gold and Silver)"]
    c_h1, c_h2 = st.columns(2)
    with c_h1:
        st.markdown("**The 3 Mandatory Hallmarks on Gold Jewellery:**")
        for mark in h_info["three_hallmarks"]:
            st.markdown(f"- {mark}")
        st.markdown("**Notified Purity Grades:**")
        st.markdown("- **24K (995 ppt)**: 99.5% pure gold")
        st.markdown("- **22K (916 ppt)**: 91.6% pure gold (Most common for jewellery)")
        st.markdown("- **18K (750 ppt)**: 75.0% pure gold")
        st.markdown("- **14K (585 ppt)**: 58.5% pure gold")
    with c_h2:
        st.markdown("**Consumer Verification via BIS Care App:**")
        st.write(h_info["consumer_verification"])
        st.markdown("""
        ```text
        [BIS Triangle Logo] + [22K916] + [6-Digit HUID: e.g. AB12CD]
        ```
        Every jewellery item has a unique laser-stamped HUID code that ties it to the registered jeweller, hallmarking centre, and purity test.
        """)

    st.divider()
    st.markdown("### 3. BIS Central & Regional Laboratories Network")
    st.markdown("Recognized laboratories where compliance testing is conducted:")
    for lab in BIS_LABORATORIES:
        with st.expander(f"{lab['name']} - {lab['location']}"):
            st.write(lab["capabilities"])

    st.divider()
    st.markdown("### 4. Consumer Rights & Grievance Redressal")
    for s_name, s_val in CONSUMER_SERVICES.items():
        st.markdown(f"- **{s_name}**: {s_val}")
