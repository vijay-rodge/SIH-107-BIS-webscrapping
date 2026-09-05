"""
Tab 4 View: BIS Certification Schemes, Hallmarking HUID, and Testing Laboratories Guide
"""

import streamlit as st
from bis_knowledge import BIS_SCHEMES, BIS_LABORATORIES, CONSUMER_SERVICES

def render_tab_guide():
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

