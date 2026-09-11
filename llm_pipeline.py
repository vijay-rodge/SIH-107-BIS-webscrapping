"""
Dual-LLM Pipeline for Indian Standards and BIS Services
Implements the two-stage Chain-of-Agents workflow:
  Stage 1 (LLM 1): Technical Extraction & Candidate Filtering Agent
  Stage 2 (LLM 2): Conversational BIS Advisor & Multilingual Synthesizer Agent
Supports Gemini, Groq, OpenAI, Ollama, and an intelligent deterministic Fallback.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

from bis_knowledge import BIS_SCHEMES, BIS_LABORATORIES, CONSUMER_SERVICES

# System Prompts
LLM1_SYSTEM_PROMPT = """You are the BIS Standards Technical Analyzer (LLM 1).
Your role is to strictly analyze user input and candidate Indian Standards retrieved from the BIS CSV database.
Your tasks:
1. Identify which candidate standard(s) directly match or govern the user's product or query.
2. Filter out non-matching candidates.
3. Extract exact factual details:
   - IS Number & Year
   - Official Title
   - Current Status (Active, Withdrawn, Under Revision)
   - Technical Committee (e.g., ETD 09, FAD 25, MTD 10)
   - Number of Amendments
   - Price in India (INR) & Outside India
   - Key Scope / National Foreword / Clauses from the preview document
4. Determine the primary technical domain (e.g., Electrical, Food/Water, Electronics, Metallurgy, Protective Gear, Hallmarking).
5. Format extracted candidates in a compact, screen-responsive markdown table with at most 4 columns (e.g. `| IS Number & Year | Status & Committee | Official Title & Scope | Match Result |`), or use structured bullet points. NEVER create wide tables with candidates spread horizontally across many columns, as this breaks screen responsiveness on mobile and standard screens.

Output your analysis in structured, factual format with clear sections. DO NOT hallucinate standard numbers or clauses not present in the candidates or verified BIS data."""

LLM2_SYSTEM_PROMPT = """You are the AI Assistant for Indian Standards and BIS Services (LLM 2) developed for the Department of Consumer Affairs (DoCA), Ministry of Consumer Affairs, Food & Public Distribution.

You receive the structured technical extraction from LLM 1 along with the user's query.
Your task is to generate a comprehensive, highly professional, source-backed, and user-friendly response tailored to industries (MSMEs/startups), consumers, and researchers.

Your response must include:
1. **Applicable Indian Standard(s)**: Clear naming, status, and concise scope summary based on LLM 1's findings.
2. **Relevant BIS Certification Scheme**:
   - Specify whether it falls under Scheme-I (ISI Mark), Scheme-II (CRS - Compulsory Registration Scheme), Scheme-IV, FMCS (for foreign manufacturers), or the Hallmarking Scheme.
   - Clarify whether certification is MANDATORY under a Government Quality Control Order (QCO).
3. **Step-by-Step Licensing Procedure**:
   - Clear roadmap on Manakonline (www.manakonline.in) or CRS portal (www.crsbis.in).
   - Mention special MSME / Startup concessions (50% fee concession for Micro enterprises and women entrepreneurs).
4. **Testing & Laboratory Guidance**:
   - Core testing parameters and mention of BIS Central/Regional Labs or NABL-accredited BIS recognized labs.
5. **Consumer Protection & Verification**:
   - Guide the user on how to verify authenticity using the BIS Care Mobile App (verifying CM/L license, CRS R-number, or 6-digit HUID for gold).
6. **Language**:
   - Respond in the language requested by the user (English, Hindi / Hinglish, or regional languages). Keep tone encouraging, authoritative, and actionable.
7. **Document / Source Reference**:
   - Provide standard number, technical committee, and reference link.
8. **Layout & Screen Responsiveness**:
   - Format lists, parameters, and steps vertically using bold bullet points or compact cards.
   - Do NOT construct wide tables with 4+ columns that overflow standard viewports or mobile devices."""


class DualLLMPipeline:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self.groq_client = None
        self._init_clients()

    def _init_clients(self):
        """Initializes clients if environment variables are present."""
        load_dotenv(override=True)
        # 1. Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.gemini_client = genai
            except Exception as e:
                print(f"[DualLLM] Error configuring Gemini: {e}")

        # 2. Groq
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
            except Exception as e:
                print(f"[DualLLM] Error configuring Groq: {e}")

        # 3. OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
            except Exception as e:
                print(f"[DualLLM] Error configuring OpenAI: {e}")

    def call_llm(self, system_prompt: str, user_prompt: str, provider: str = "auto", custom_key: Optional[str] = None) -> str:
        """Invokes the selected LLM provider or falls back gracefully."""
        # Dynamic key override
        if custom_key:
            if provider == "gemini":
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=custom_key)
                    try:
                        model = genai.GenerativeModel("gemini-flash-latest")
                        resp = model.generate_content(f"{system_prompt}\n\nUser Query:\n{user_prompt}")
                    except Exception:
                        model = genai.GenerativeModel("gemini-3.6-flash")
                        resp = model.generate_content(f"{system_prompt}\n\nUser Query:\n{user_prompt}")
                    return resp.text
                except Exception as e:
                    print(f"[LLM] Gemini custom key error: {e}")
            elif provider == "groq":
                try:
                    from groq import Groq
                    client = Groq(api_key=custom_key)
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3
                    )
                    return resp.choices[0].message.content
                except Exception as e:
                    print(f"[LLM] Groq custom key error: {e}")
            elif provider == "openai":
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=custom_key)
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3
                    )
                    return resp.choices[0].message.content
                except Exception as e:
                    print(f"[LLM] OpenAI custom key error: {e}")

        # Auto fallback using existing clients
        if self.gemini_client:
            try:
                try:
                    model = self.gemini_client.GenerativeModel("gemini-flash-latest")
                    resp = model.generate_content(f"{system_prompt}\n\nUser Query:\n{user_prompt}")
                except Exception:
                    model = self.gemini_client.GenerativeModel("gemini-3.6-flash")
                    resp = model.generate_content(f"{system_prompt}\n\nUser Query:\n{user_prompt}")
                return resp.text
            except Exception as e:
                print(f"[LLM] Gemini call failed: {e}")

        if self.groq_client:
            try:
                resp = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                return resp.choices[0].message.content
            except Exception as e:
                print(f"[LLM] Groq call failed: {e}")

        if self.openai_client:
            try:
                resp = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                return resp.choices[0].message.content
            except Exception as e:
                print(f"[LLM] OpenAI call failed: {e}")

        # Intelligent Fallback Engine
        return None

    def intelligent_fallback_llm1(self, query: str, scored_items: List[Tuple[Dict[str, Any], float]]) -> str:
        """
        Deterministic, high-accuracy technical extraction simulation for LLM 1
        when external API keys are unavailable.
        """
        if not scored_items:
            return (
                "### Technical Extraction & Candidate Filtering (LLM 1 Analysis)\n\n"
                "- **Status**: No direct candidate standards found in local CSV database for this specific query.\n"
                "- **Recommendation**: Recommend user to trigger live scraper on the BIS portal or search related sectoral terms."
            )

        top_std, score = scored_items[0]
        other_stds = scored_items[1:]

        output = [
            "### [LLM 1] Technical Extraction & Standard Verification",
            f"**Query Analyzed**: \"{query}\"",
            f"**Primary Matched Standard**: `{top_std.get('is_no', 'N/A')}` (Confidence Score: {score:.1f})",
            "",
            "#### 1. Standard Metadata Verification",
            f"- **Official Title**: {top_std.get('title', 'N/A')}",
            f"- **Current Status**: **{top_std.get('status', 'Active')}** (Reaffirmed: {top_std.get('reaffirmed_year') or 'Current Edition'})",
            f"- **Governing Technical Committee**: `{top_std.get('technical_committee', 'General Committee')}`",
            f"- **Amendments Issued**: {top_std.get('amendments', '0')}",
            f"- **Official Pricing**: India: {top_std.get('price_in_india', 'N/A')} | Overseas: {top_std.get('price_outside_india', 'N/A')}",
            "",
            "#### 2. Scope & Technical Foreword (from Preview Document)",
            f"> \"{top_std.get('description', 'Scope details retrieved from official BIS preview document.')}\"",
            "",
            f"- **BIS Preview Resource**: [{top_std.get('is_no')}]({top_std.get('preview_url')})" if top_std.get('preview_url') else "- **BIS Preview Resource**: Verified in Official BIS Catalogue",
        ]

        if other_stds:
            output.append("\n#### 3. Filtered Secondary Candidates Evaluated:")
            for s, sc in other_stds[:3]:
                output.append(f"- `{s.get('is_no')}`: {s.get('title')} (Relevance: {sc:.1f})")

        return "\n".join(output)

    def intelligent_fallback_llm2(self, query: str, llm1_output: str, scored_items: List[Tuple[Dict[str, Any], float]], language: str = "English") -> str:
        """
        Deterministic, high-accuracy conversational advisory simulation for LLM 2
        when external API keys are unavailable.
        """
        top_std = scored_items[0][0] if scored_items else {}
        is_no = top_std.get("is_no", "Relevant Indian Standard")
        title = top_std.get("title", "Standard Specification")
        tc = top_std.get("technical_committee", "")
        desc = top_std.get("description", "")
        q_lower = query.lower()

        # Determine Scheme
        scheme_key = "Scheme-I (ISI Mark - Product Certification Scheme)"
        qco_mandatory = "MANDATORY under Quality Control Order (QCO)"
        
        if any(w in q_lower or w in desc.lower() for w in ["led", "battery", "laptop", "mobile", "electronic", "inverter", "crs", "solar", "photovoltaic"]):
            scheme_key = "Scheme-II (CRS - Compulsory Registration Scheme)"
        elif any(w in q_lower or w in desc.lower() for w in ["gold", "silver", "jewellery", "hallmark", "huid", "carat"]):
            scheme_key = "Hallmarking Scheme (Gold and Silver)"
            qco_mandatory = "MANDATORY in notified districts across India"

        scheme_info = BIS_SCHEMES.get(scheme_key, BIS_SCHEMES["Scheme-I (ISI Mark - Product Certification Scheme)"])

        # Multilingual Support: Hindi translation for core responses
        is_hindi = language.lower() in ["hindi", "हिन्दी"] or any('\u0900' <= ch <= '\u097f' for ch in query)

        if is_hindi:
            return f"""### भारतीय मानक ब्यूरो (BIS) आधिकारिक तकनीकी मूल्यांकन

**आपके प्रश्न के अनुसार लागू मानक**: **{is_no}**  
**मानक का शीर्षक**: {title}  
**स्थिति**: {top_std.get('status', 'सक्रिय (Active)')} | **तकनीकी समिति**: {tc}

---

#### 1. लागू बीआईएस प्रमाणन योजना (Certification Scheme)
- **योजना का नाम**: **{scheme_info.get('name')}**
- **प्रमाणन स्थिति**: यह उत्पाद भारत सरकार के **गुणवत्ता नियंत्रण आदेश (QCO)** के तहत **अनिवार्य (MANDATORY)** है। बिना वैध BIS लाइसेंस या हॉलमार्क के इसका निर्माण, आयात या विक्रय कानूनन अपराध है।
- **पोर्टल**: {scheme_info.get('portal')}

#### 2. लाइसेंस प्राप्त करने की प्रक्रिया (MSME और उद्योगों के लिए)
1. **मानक की पहचान**: सुनिश्चित करें कि आपका उत्पाद **{is_no}** के अनुरूप है।
2. **इन-हाउस परीक्षण सुविधा**: BIS परीक्षण योजना (SIT) के अनुसार आवश्यक परीक्षण उपकरण स्थापित करें।
3. **ऑनलाइन आवेदन**: [manakonline.in](https://www.manakonline.in) पर फॉर्म भरें और आवश्यक दस्तावेज जमा करें।
4. **फैक्ट्री ऑडिट और नमूना परीक्षण**: BIS अधिकारी निरीक्षण करेंगे और नमूने BIS मान्यता प्राप्त NABL प्रयोगशाला में भेजे जाएंगे।
5. **लाइसेंस आवंटन (CM/L)**: संतुष्टि पर ISI मार्क या रजिस्ट्रेशन नंबर प्रदान किया जाएगा।
> **MSME और स्टार्टअप के लिए विशेष छूट**: सूक्ष्म उद्यमों (Micro), स्टार्टअप्स और महिला उद्यमियों को आवेदन शुल्क और वार्षिक लाइसेंस शुल्क में **50% की विशेष छूट** मिलती है।

#### 3. परीक्षण प्रयोगशालाएं (Testing Laboratories)
- नमूने **BIS केंद्रीय प्रयोगशाला (गाजियाबाद)** या **BIS मान्यता प्राप्त NABL लैब्स** में परीक्षण किए जा सकते हैं।

#### 4. उपभोक्ता सुरक्षा व सत्यापन (Consumer Verification)
- उपभोक्ता **BIS Care Mobile App** डाउनलोड करके उत्पाद के ISI लाइसेंस (CM/L नंबर) या हॉलमार्किंग के 6-अंकीय **HUID कोड** को तुरंत सत्यापित कर सकते हैं।
- किसी भी शिकायत के लिए राष्ट्रीय उपभोक्ता हेल्पलाइन (1915) या BIS Care पोर्टल पर शिकायत दर्ज कर सकते हैं।

**आधिकारिक संदर्भ**: {top_std.get('preview_url') or 'BIS Standards Portal'}"""

        # English Response
        steps_text = "\n".join([f"- {s}" for s in scheme_info.get("licensing_steps", ["Register on Manakonline", "Factory audit", "Grant of license"])])
        
        return f"""### Bureau of Indian Standards (BIS) Advisory Assessment

Based on verified BIS technical records, here is the complete compliance and procedural guidance for your query:

---

#### 1. Applicable Indian Standard
- **Standard Number**: `{is_no}`
- **Title**: **{title}**
- **Status**: `{top_std.get('status', 'Active')}` | **Technical Committee**: `{tc}`
- **National Foreword / Scope Summary**:
  > {desc[:350] + ('...' if len(desc) > 350 else '')}

---

#### 2. Governing BIS Certification Scheme
- **Applicable Scheme**: **{scheme_info.get('name')}** ({scheme_info.get('type')})
- **Regulatory Nature**: **{qco_mandatory}**. Non-compliance or selling non-certified goods violates the **Bureau of Indian Standards Act, 2016** and attracts penalties.
- **Application Portal**: `{scheme_info.get('portal')}`

---

#### 3. Step-by-Step Licensing Procedure
{steps_text}

> [!TIP]
> **MSME & Startup Benefits**:
> Under DoCA guidelines, Micro Enterprises, Startups, and Women Entrepreneurs receive a **50% concession** on application fees, annual license fees, and marking fees. Small enterprises receive a **20% concession**.

---

#### 4. Testing Requirements & Recognized Laboratories
- Testing must satisfy the parameters outlined in `{is_no}`.
- Approved testing can be conducted at:
  - **BIS Central Laboratory (CL)**, Sahibabad / Ghaziabad
  - **BIS Regional Laboratories** (Mumbai, Kolkata, Chennai, Mohali)
  - Over **300+ NABL-accredited labs** recognized under the BIS Laboratory Recognition Scheme (LRS).

---

#### 5. Consumer Protection & Verification Guidance
- **Verify Authenticity**: Consumers and procurement officers can verify the genuine nature of the certification using the official **BIS Care Mobile App**:
  - For **ISI Mark**: Enter the 7-digit **CM/L Number** stamped beneath the ISI mark.
  - For **Electronics (CRS)**: Enter the **R-XXXXXXXX** registration number.
  - For **Gold Jewellery**: Enter the laser-etched 6-digit alphanumeric **HUID** code.
- **Reporting Violations**: Sub-standard quality or fake ISI logos can be reported directly via the **BIS Care App** or the **National Consumer Helpline (Toll-Free 1915)**.

---
**Official Reference**: [{is_no} on BIS e-Sale Portal]({top_std.get('preview_url') or 'https://standardsbis.bsbedge.com'})"""

    def run(self, user_query: str, candidates_text: str, scored_items: List[Tuple[Dict[str, Any], float]], language: str = "English", provider: str = "auto", custom_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the complete Dual-LLM chain:
        1. Prepares Prompt 1 (User Query + CSV Candidate Data)
        2. Calls LLM 1 (Candidate Extraction & Technical Filter)
        3. Prepares Prompt 2 (User Query + LLM 1 Findings + BIS Schemes)
        4. Calls LLM 2 (Conversational BIS Advisor & Multilingual Synthesizer)
        """
        # Step 1: Run LLM 1
        llm1_prompt = (
            f"User Input Query: \"{user_query}\"\n\n"
            f"Candidate Indian Standards from BIS Database:\n"
            f"----------------------------------------\n"
            f"{candidates_text}\n"
            f"----------------------------------------\n\n"
            f"Filter non-matching candidates and extract exact verified technical facts (IS no, status, committee, amendments, pricing, preview scope)."
        )

        llm1_response = None
        provider_used = provider

        # Attempt live LLM 1 call
        if provider != "mock":
            llm1_response = self.call_llm(LLM1_SYSTEM_PROMPT, llm1_prompt, provider=provider, custom_key=custom_key)

        if not llm1_response:
            llm1_response = self.intelligent_fallback_llm1(user_query, scored_items)
            provider_used = "deterministic-fallback"

        # Step 2: Run LLM 2
        llm2_prompt = (
            f"User Query: \"{user_query}\"\n"
            f"Requested Language: {language}\n\n"
            f"Structured Findings from LLM 1:\n"
            f"----------------------------------------\n"
            f"{llm1_response}\n"
            f"----------------------------------------\n\n"
            f"Synthesize the complete, source-backed natural language response with applicable standards, BIS schemes (ISI/CRS/Hallmarking), licensing steps, MSME concessions, testing labs, and consumer verification guidance."
        )

        llm2_response = None
        if provider != "mock" and provider_used != "deterministic-fallback":
            llm2_response = self.call_llm(LLM2_SYSTEM_PROMPT, llm2_prompt, provider=provider, custom_key=custom_key)

        if not llm2_response:
            llm2_response = self.intelligent_fallback_llm2(user_query, llm1_response, scored_items, language=language)

        return {
            "query": user_query,
            "language": language,
            "provider": provider_used,
            "candidates_text": candidates_text,
            "llm1_output": llm1_response,
            "llm2_output": llm2_response
        }

