"""
Reusable UI Components for BIS AI Assistant
Handles header banner, sidebar emblem, CSS loading, and badge cards.
"""

import os
import streamlit as st

def load_css(css_path: str = "static/style.css"):
    """Loads and injects the external stylesheet into Streamlit."""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        print(f"[UI] Warning: CSS file not found at {css_path}")

def render_sidebar_logo():
    """Renders the official BIS / DoCA vector emblem in the sidebar."""
    st.markdown("""
    <div class="sidebar-logo-card">
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

def render_header():
    """Renders the main government portal header card."""
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

def render_loop_badge(user_query: str, scraped_count: int, newly_saved_count: int, provider_used: str):
    """Renders execution status badge for an automated search-and-scrape cycle."""
    st.markdown(f"""
    <div class="loop-badge">
        <b>Execution Complete for:</b> "{user_query}" | 
        <b>Scraped from Web:</b> {scraped_count} | 
        <b>Saved to CSV:</b> +{newly_saved_count} | 
        <b>Engine:</b> {provider_used}
    </div>
    """, unsafe_allow_html=True)

