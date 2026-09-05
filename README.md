# 🏛️ AI-Powered Intelligent Assistant for Indian Standards & BIS Services
### **Smart India Hackathon (SIH) | Problem Statement ID: 26107**
**Organization**: Ministry of Consumer Affairs, Food & Public Distribution  
**Department**: Department of Consumer Affairs (DoCA)  
**Theme**: Smart Automation  

---

## 📌 Problem Overview
The **Bureau of Indian Standards (BIS)** publishes thousands of Indian Standards and operates conformity assessment schemes (ISI Mark Scheme-I, CRS Scheme-II, FMCS, Hallmarking, Lab Recognition). Micro, Small & Medium Enterprises (MSMEs), startups, students, and consumers often struggle to:
- Identify applicable Indian Standards (IS) for products.
- Determine whether a standard is mandatory under a **Quality Control Order (QCO)**.
- Understand licensing procedures (Manakonline / e-BIS) and concessions (50% fee concession for Micro/Startups).
- Find authorized testing laboratories (Central Labs, Regional Labs, NABL recognized).
- Navigate Gold/Silver Hallmarking requirements and 6-digit **HUID** verification.
- Obtain technical answers with exact clause and foreword citations.

---

## Project Directory Structure

```text
csv_approach/
├── .env                      # Environment API keys (Gemini, Groq, OpenAI)
├── .env.example              # Clean deployment template
├── requirements.txt          # Production dependencies
├── README.md                 # Project documentation
├── app.py                    # Clean Streamlit production entrypoint
│
├── static/                   # Static styling assets
│   └── style.css             # Modular production stylesheet
│
├── ui/                       # Modular UI views and components
│   ├── __init__.py
│   ├── components.py         # Reusable headers, emblem, badges, CSS loader
│   ├── tab_chat.py           # Tab 1: Conversational Assistant & Loop Inspector
│   ├── tab_scraper.py        # Tab 2: Manual Standards Scraper
│   ├── tab_database.py       # Tab 3: CSV Database Explorer & Details Inspector
│   └── tab_guide.py          # Tab 4: BIS Schemes, Hallmarking & Lab Guides
│
├── search_loop.py            # Automated Live Loop: Search -> Scrape -> CSV -> LLM 1 -> LLM 2
├── scraper.py                # BIS Web Scraper & Preview Extractor
├── retriever.py              # CSV Query Matcher & Relevance Ranker
├── llm_pipeline.py           # Dual-LLM Pipeline Orchestrator (LLM 1 & LLM 2)
├── bis_knowledge.py          # BIS Schemes, Lab Directory, Regulations Knowledge Base
├── seed_database.py          # Flagship and live database seeder
├── cli_loop.py               # Terminal interactive loop runner
└── standards_data.csv        # Primary Indian Standards knowledge base
```

```
[ User Query / Product Name ]
          │
          ▼
[ Keyword & IS No. Matcher ] ──▶ Queries ──▶ [ standards_data.csv ]
                                                    ▲
                                                    │ Scraped & Enriched
                                           [ standardsbis.bsbedge.com ]
                                           [ & BIS_Preview.aspx API  ]
          │
          ▼
[ Candidate Standards + System Prompt ]
          │
          ▼
[ LLM 1: Technical Extraction & Filter Agent ]
   • Validates active/withdrawn status & reaffirmation
   • Extracts committee codes (ETD, FAD, MTD, etc.)
   • Gathers National Foreword, Scope & Pricing
          │
          ▼
[ LLM 2: Conversational BIS Services Advisor ]
   • Generates plain-language, source-backed explanation
   • Identifies BIS Scheme (Scheme-I ISI Mark, Scheme-II CRS, Hallmarking)
   • Outlines licensing roadmap on Manakonline with MSME concessions
   • Specifies laboratory testing parameters
   • Provides consumer guidance & BIS Care verification (HUID/CML)
   • Delivers in preferred language (English, Hindi, etc.)
          │
          ▼
[ Interactive Web Application (Streamlit) ]
```

---

## 🌟 Key Features

1. **Live BIS Portal Web Scraper & Preview Extractor (`scraper.py`)**:
   - Queries `standardsbis.bsbedge.com/BIS_SearchStandard.aspx?keyword={keyword}&id=0`.
   - Captures all table/repeater fields: `IS no.`, `title`, `status`, `technical committee`, `amendments`, `price within india`, `price outside india`.
   - Queries the backend preview document endpoint (`BIS_Preview.aspx?id=...`) to parse the HTML document, National Foreword, and Scope.
   - Automatically maintains and deduplicates records in `standards_data.csv`.

2. **Dual-LLM Chain-of-Agents Pipeline (`llm_pipeline.py`)**:
   - **LLM 1 (Candidate Extractor)**: Factual technical filter eliminating hallucinations.
   - **LLM 2 (Conversational Advisor)**: Domain-expert advisor explaining schemes, labs, and licensing.
   - **Multi-Model Support**: Works with Google Gemini, Groq (Llama 3.3), OpenAI (GPT-4o), and local Ollama.
   - **Deterministic Fallback Engine**: Works immediately out-of-the-box without requiring an API key.

3. **Domain Knowledge Engine (`bis_knowledge.py`)**:
   - Complete guides for **Scheme-I (ISI Mark)**, **Scheme-II (CRS)**, **Scheme-IV**, **FMCS**, and **Hallmarking (HUID)**.
   - Official testing lab directory (BIS Central Lab Sahibabad, Regional Labs in Mumbai, Kolkata, Chennai, Mohali, and NABL labs).
   - Consumer redressal (BIS Care Mobile App, National Consumer Helpline 1915).

4. **Interactive Web Application (`app.py`)**:
   - **Conversational Assistant Tab**: Natural language chat with side-by-side Dual-LLM inspector.
   - **Live BIS Scraper Tab**: On-demand scraping of new standards from the official portal.
   - **Standards Database Explorer**: Filter, search, and download `standards_data.csv`.
   - **BIS Schemes & Hallmarking Guide**: Educational reference for industries and consumers.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Quick Test Scenarios

| Domain / Query | Expected Standard | Scheme | Key Feature |
| :--- | :--- | :--- | :--- |
| **Packaged Drinking Water** | `IS 14543 : 2016` | Scheme-I (ISI Mark) | Mandatory QCO; microbiological and pesticide testing |
| **Gold Jewellery Hallmarking** | `IS 1417 : 2016` | Hallmarking Scheme | 6-digit HUID code, 22K916 purity mark, BIS Care App verification |
| **Self-Ballasted LED Lamps** | `IS 16102 : 2012` | Scheme-II (CRS) | Self-declaration of conformity, CRS registration |
| **Protective Helmets for Two-Wheelers** | `IS 4151 : 2020` | Scheme-I (ISI Mark) | MoRTH QCO; impact attenuation and penetration tests |
| **Safety of Toys** | `IS 9873 : 2019` | Scheme-I (ISI Mark) | Mechanical safety, toxic metal migration limits |
| **High Voltage Transmission** | `IS 1885 : Part 30` | Standards Reference | Vocabulary and technical committee ETD 01 |

