"""
Tab 3 View: Standards Knowledge Base CSV Explorer & Details Inspector
"""

import os
import pandas as pd
import streamlit as st

def render_tab_database(csv_file: str):
    st.subheader("Standards Knowledge Base Explorer")
    st.caption(f"Browsing `{csv_file}` (dynamically updated by every search-and-scrape cycle).")

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        
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
            width="stretch"
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

