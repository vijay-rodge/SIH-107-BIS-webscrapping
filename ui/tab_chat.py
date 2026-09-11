"""
Tab 1 View: Conversational Assistant & Dual-LLM Search Loop Inspector
"""

import streamlit as st
from search_loop import BISSearchLoop
from ui.components import render_loop_badge

def render_tab_chat(
    search_loop: BISSearchLoop,
    language: str,
    provider_choice: str,
    custom_api_key: str,
    max_scrape_per_query: int,
    live_scrape_enabled: bool
):
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
            if cols_btn[i].button(label, key=f"quick_btn_{i}", width="stretch"):
                clicked_query = query_text
                st.session_state["user_query_input"] = query_text

        # Search Form to enable pressing Enter to submit
        with st.form(key="search_form", clear_on_submit=False):
            default_val = clicked_query if clicked_query else st.session_state.get("user_query_input", "")
            user_query = st.text_input(
                "Enter Keyword, Product, or IS Number:",
                value=default_val,
                placeholder="e.g., IS 10500, IS 138, pressure cooker, battery charger, solar inverter...",
                key="user_query_input"
            )
            submit_btn = st.form_submit_button("Search and Analyze", type="primary", width="stretch")

        if submit_btn and not user_query.strip():
            st.warning("Please enter an IS number, product name, or keyword before searching.")

    with col_inspect:
        st.subheader("Automated Loop & Pipeline Inspector")
        st.caption("Live tracking of each step in the workflow loop:")
        st.info("Webpage Search ➔ Scrape Data & HTML Doc ➔ Store in CSV ➔ LLM 1 (Filter) ➔ LLM 2 (Advisor)")

    # Determine query to execute (either from quick click or text submission)
    query_to_run = None
    if clicked_query:
        query_to_run = clicked_query
    elif submit_btn and user_query.strip():
        query_to_run = user_query.strip()

    if query_to_run:
        with st.spinner(f"Executing Automated Search, Scrape, and Dual-LLM Loop for '{query_to_run}'..."):
            prov_map = {
                "Auto / Fallback Engine": "auto",
                "Google Gemini": "gemini",
                "Groq (Llama 3.3)": "groq",
                "OpenAI (GPT-4o)": "openai"
            }
            chosen_prov = prov_map.get(provider_choice, "auto")

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
            render_loop_badge(
                user_query=latest["user_query"],
                scraped_count=latest["scraped_count"],
                newly_saved_count=latest["newly_saved_count"],
                provider_used=latest["provider_used"]
            )
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

