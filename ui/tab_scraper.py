"""
Tab 2 View: Manual Standards Web Scraper
Allows on-demand scraping of any keyword or IS Number from standardsbis.bsbedge.com
"""

import pandas as pd
import streamlit as st
from scraper import save_to_csv
from search_loop import BISSearchLoop

def render_tab_scraper(search_loop: BISSearchLoop, csv_file: str):
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
                added = save_to_csv(items, csv_file, append=True)
                search_loop.retriever.load_data()  # refresh retriever cache
                st.success(f"Successfully scraped {len(items)} items ({'IS Number Search' if is_std else 'Keyword Search'})! Added {added} new unique standard(s) to '{csv_file}'.")
                
                df_scraped = pd.DataFrame(items)
                st.dataframe(df_scraped[["is_no", "title", "status", "technical_committee", "price_in_india", "price_outside_india", "preview_id"]], use_container_width=True)
            else:
                st.warning("No standards found on the live portal for this keyword, or server connection timed out.")

