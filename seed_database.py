"""
Seed Script for BIS Standards Database
Scrapes key categories from standardsbis.bsbedge.com, enriches with preview descriptions,
and ensures essential flagship standards across all SIH problem domains are present in standards_data.csv.
"""

import os
import sys
import io
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scraper import BISScraper, save_to_csv

CSV_FILE = "standards_data.csv"

# Essential Flagship Standards spanning BIS Schemes, QCOs, Consumer Goods, and Hallmarking
FLAGSHIP_STANDARDS = [
    {
        "is_no": "IS 10500 : 2012",
        "title": "Drinking Water - Specification (Second Revision)",
        "status": "Active",
        "technical_committee": "FAD 25 (Drinking Water)",
        "amendments": "3",
        "reaffirmed_year": "2023",
        "price_in_india": "₹ 790.00",
        "price_outside_india": "₹ 7,900.00",
        "description": "ICS 13.060.20 FAD 25. NATIONAL FOREWORD: This Indian Standard (Second Revision) was adopted by the Bureau of Indian Standards after the draft finalized by the Drinking Water Sectional Committee had been approved by the Food and Agriculture Division Council. This standard prescribes the requirements and methods of sampling and test for drinking water (potable water) supplied through piped network, tankers, packaged drinking water, or ground sources. Key test parameters include physical, organoleptic, chemical, toxic substances, and bacteriological requirements (E. coli, coliforms). Mandatory under Scheme I for packaged drinking water (IS 14543) and packaged natural mineral water (IS 13428).",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=10500",
        "preview_id": "10500"
    },
    {
        "is_no": "IS 14543 : 2016",
        "title": "Packaged Drinking Water (Other Than Packaged Natural Mineral Water) - Specification (Second Revision)",
        "status": "Active",
        "technical_committee": "FAD 25 (Drinking Water)",
        "amendments": "4",
        "reaffirmed_year": "2021",
        "price_in_india": "₹ 620.00",
        "price_outside_india": "₹ 6,200.00",
        "description": "FAD 25. National Foreword: Prescribes the quality requirements and methods of sampling and testing for packaged drinking water other than packaged natural mineral water. Mandatory under BIS Scheme I (ISI Mark) and Food Safety and Standards Authority of India (FSSAI) regulations. Manufacturers must hold a valid BIS license before commercial production and sale. Requires testing for physical characteristics, pesticide residues, microbiological contaminants, and packaging containers conforming to food-grade plastics.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=14543",
        "preview_id": "14543"
    },
    {
        "is_no": "IS 1417 : 2016",
        "title": "Gold and Gold Alloys, Jewellery/Artefacts - Fineness and Marking - Specification (Fourth Revision)",
        "status": "Active",
        "technical_committee": "MTD 10 (Precious Metals)",
        "amendments": "2",
        "reaffirmed_year": "2021",
        "price_in_india": "₹ 430.00",
        "price_outside_india": "₹ 4,300.00",
        "description": "ICS 39.060 MTD 10. National Foreword: Specifies requirements for gold alloys and fine gold jewellery/artefacts regarding fineness in parts per thousand (ppt) and their hallmarking. Recognized grades: 24K (995), 23K (958), 22K (916), 20K (833), 18K (750), and 14K (585). Hallmarking consists of three marks: BIS Logo, Purity/Fineness in carat & ppt (e.g., 22K916), and 6-digit alphanumeric Hallmark Unique Identification (HUID) code. Mandatory Hallmarking applies across notified districts in India under the BIS Hallmarking Scheme.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=1417",
        "preview_id": "1417"
    },
    {
        "is_no": "IS 2112 : 2014",
        "title": "Silver and Silver Alloys, Jewellery/Artefacts - Fineness and Marking - Specification",
        "status": "Active",
        "technical_committee": "MTD 10 (Precious Metals)",
        "amendments": "1",
        "reaffirmed_year": "2020",
        "price_in_india": "₹ 340.00",
        "price_outside_india": "₹ 3,400.00",
        "description": "ICS 39.060 MTD 10. Prescribes the purity grades and hallmarking guidelines for silver jewellery and artefacts. Common grades include 990, 925 (Sterling Silver), 900, 835, and 800 parts per thousand. Governed under the BIS Hallmarking Scheme for Assaying and Hallmarking Centres (AHC).",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=2112",
        "preview_id": "2112"
    },
    {
        "is_no": "IS 694 : 2010",
        "title": "Polyvinyl Chloride Insulated Unsheathed and Sheathed Cables/Cords with Rigid and Flexible Conductor for Working Voltages Up to and Including 450/750 V",
        "status": "Active",
        "technical_committee": "ETD 09 (Power Cables)",
        "amendments": "2",
        "reaffirmed_year": "2020",
        "price_in_india": "₹ 880.00",
        "price_outside_india": "₹ 8,800.00",
        "description": "ICS 29.060.20 ETD 09. Specifies the constructional and testing requirements for PVC insulated single-core and multi-core cables and flexible cords for household wiring and industrial distribution up to 1100 V. Mandatory ISI Mark under the Electrical Wires and Cables (Quality Control) Order. Mandatory testing includes insulation resistance, spark test, conductor resistance, tensile strength, and flame retardancy tests.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=694",
        "preview_id": "694"
    },
    {
        "is_no": "IS 16102 : Part 1 : 2012",
        "title": "Self-Ballasted LED Lamps for General Lighting Services - Part 1 Safety Requirements",
        "status": "Active",
        "technical_committee": "ETD 23 (Electric Lamps and their Auxiliaries)",
        "amendments": "3",
        "reaffirmed_year": "2022",
        "price_in_india": "₹ 520.00",
        "price_outside_india": "₹ 5,200.00",
        "description": "ICS 29.140.99 ETD 23. Specifies safety and interchangeability requirements for self-ballasted LED lamps with integrated means for controlling electrical operation, intended for domestic and similar general lighting purposes. Governed under BIS Scheme II - Compulsory Registration Scheme (CRS) administered by MeitY and BIS. Manufacturers must test products in BIS-recognized labs and register online via CRS portal.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=16102_1",
        "preview_id": "16102_1"
    },
    {
        "is_no": "IS 16102 : Part 2 : 2012",
        "title": "Self-Ballasted LED Lamps for General Lighting Services - Part 2 Performance Requirements",
        "status": "Active",
        "technical_committee": "ETD 23 (Electric Lamps and their Auxiliaries)",
        "amendments": "2",
        "reaffirmed_year": "2022",
        "price_in_india": "₹ 480.00",
        "price_outside_india": "₹ 4,800.00",
        "description": "ICS 29.140.99 ETD 23. Specifies performance requirements, lumen maintenance, luminous efficacy, color rendering index (CRI), correlated color temperature (CCT), and life testing for LED lamps used in general lighting.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=16102_2",
        "preview_id": "16102_2"
    },
    {
        "is_no": "IS 4151 : 2020",
        "title": "Protective Helmets for Two Wheeler Riders - Specification (Fourth Revision)",
        "status": "Active",
        "technical_committee": "TXD 14 (Speciality Fabrics and Protective Clothing)",
        "amendments": "1",
        "reaffirmed_year": "2024",
        "price_in_india": "₹ 680.00",
        "price_outside_india": "₹ 6,800.00",
        "description": "ICS 13.340.20 TXD 14. Prescribes physical and safety requirements, construction, dimensions, performance, and testing for protective helmets for riders of two-wheeled motor vehicles. Mandatory ISI Mark under Ministry of Road Transport and Highways (MoRTH) QCO. Tests include impact attenuation, dynamic retention test, penetration resistance, rigidity, and visor optical properties. Helmets without valid ISI mark cannot be manufactured or sold in India.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=4151",
        "preview_id": "4151"
    },
    {
        "is_no": "IS 9873 : Part 1 : 2019",
        "title": "Safety of Toys - Part 1 Safety Aspects Related to Mechanical and Physical Properties",
        "status": "Active",
        "technical_committee": "PCD 12 (Plastics and Toys)",
        "amendments": "1",
        "reaffirmed_year": "2024",
        "price_in_india": "₹ 920.00",
        "price_outside_india": "₹ 9,200.00",
        "description": "ICS 97.200.50 PCD 12. Specifies safety requirements and test methods for mechanical and physical properties of toys intended for use by children under 14 years. Mandatory under Toys (Quality Control) Order, 2020 under Scheme I (ISI Mark). Foreign and domestic manufacturers must obtain BIS certification prior to marketing toys in India. Enforces drop test, small parts choking hazards, sharp edges, and tension tests.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=9873_1",
        "preview_id": "9873_1"
    },
    {
        "is_no": "IS 9873 : Part 3 : 2020",
        "title": "Safety of Toys - Part 3 Migration of Certain Elements (Toxic Metals Testing)",
        "status": "Active",
        "technical_committee": "PCD 12 (Plastics and Toys)",
        "amendments": "0",
        "reaffirmed_year": "2024",
        "price_in_india": "₹ 550.00",
        "price_outside_india": "₹ 5,500.00",
        "description": "ICS 97.200.50 PCD 12. Prescribes maximum limits and methods of sampling and analysis for the migration of lead, mercury, cadmium, antimony, arsenic, barium, chromium, and selenium from accessible toy materials. Crucial compliance parameter for child health and toy manufacturing under BIS Scheme I.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=9873_3",
        "preview_id": "9873_3"
    },
    {
        "is_no": "IS 1786 : 2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement - Specification (Fourth Revision)",
        "status": "Active",
        "technical_committee": "MTD 04 (Wrought Steel Products)",
        "amendments": "3",
        "reaffirmed_year": "2023",
        "price_in_india": "₹ 740.00",
        "price_outside_india": "₹ 7,400.00",
        "description": "ICS 77.140.15 MTD 04. Specifies requirements for thermo-mechanically treated (TMT) and cold worked deformed steel bars and wires for concrete reinforcement in grades Fe 415, Fe 415D, Fe 500, Fe 500D, Fe 550, Fe 550D, Fe 600. Mandatory ISI Mark under Ministry of Steel Quality Control Order. Covers yield strength, elongation, bend and rebend tests, chemical composition, and rib geometry.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=1786",
        "preview_id": "1786"
    },
    {
        "is_no": "IS 269 : 2015",
        "title": "Ordinary Portland Cement - Specification (Sixth Revision)",
        "status": "Active",
        "technical_committee": "CED 02 (Cement and Concrete)",
        "amendments": "2",
        "reaffirmed_year": "2020",
        "price_in_india": "₹ 620.00",
        "price_outside_india": "₹ 6,200.00",
        "description": "ICS 91.100.10 CED 02. Harmonized specification covering 33 grade, 43 grade, and 53 grade ordinary Portland cement. Mandatory BIS ISI Mark under Cement (Quality Control) Order. Mandatory parameters: compressive strength at 3, 7, and 28 days, fineness (specific surface by Blaine's air permeability), soundess (Le-Chatelier and autoclave), initial and final setting times.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=269",
        "preview_id": "269"
    },
    {
        "is_no": "IS 14286 : 2010 / IEC 61215 : 2005",
        "title": "Crystalline Silicon Terrestrial Photovoltaic (PV) Modules - Design Qualification and Type Approval",
        "status": "Active",
        "technical_committee": "ETD 28 (Solar Photovoltaic Energy Systems)",
        "amendments": "1",
        "reaffirmed_year": "2021",
        "price_in_india": "₹ 1,120.00",
        "price_outside_india": "₹ 11,200.00",
        "description": "ICS 27.160 ETD 28. Sets forth requirements for the design qualification and type approval of terrestrial crystalline silicon photovoltaic modules suitable for long-term operation in general open-air climates. Mandatory under Ministry of New and Renewable Energy (MNRE) Solar Photovoltaics (Quality Control) Order under BIS Scheme II (CRS). Qualification tests include thermal cycling, damp heat, mechanical load, hail impact, and electrical insulation tests.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=14286",
        "preview_id": "14286"
    },
    {
        "is_no": "IS 16046 : Part 2 : 2018 / IEC 62133-2 : 2017",
        "title": "Secondary Cells and Batteries Containing Alkaline or Other Non-Acid Electrolytes - Safety Requirements for Portable Sealed Secondary Cells: Part 2 Lithium Systems",
        "status": "Active",
        "technical_committee": "ETD 11 (Secondary Cells and Batteries)",
        "amendments": "1",
        "reaffirmed_year": "2023",
        "price_in_india": "₹ 820.00",
        "price_outside_india": "₹ 8,200.00",
        "description": "ICS 29.220.30 ETD 11. Safety requirements for portable sealed secondary lithium cells and batteries (for use in smartphones, laptops, power banks, and portable electronics). Mandatory under Compulsory Registration Scheme (CRS - Scheme II). Tests include continuous charging at constant voltage, external short circuit, free fall, thermal abuse, crush, and overcharging.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=16046_2",
        "preview_id": "16046_2"
    },
    {
        "is_no": "IS 13252 : Part 1 : 2010 / IEC 60950-1 : 2005",
        "title": "Information Technology Equipment - Safety: Part 1 General Requirements",
        "status": "Active",
        "technical_committee": "LITD 10 (IT and Software Components)",
        "amendments": "2",
        "reaffirmed_year": "2020",
        "price_in_india": "₹ 1,840.00",
        "price_outside_india": "₹ 18,400.00",
        "description": "ICS 35.020 LITD 10. Foundational standard under MeitY's Compulsory Registration Scheme (CRS) for electronic goods: laptops, tablets, servers, printers, displays, power adapters, and POS terminals. Prescribes electrical safety, insulation resistance, creepage and clearance distances, protection against electric shock, energy hazards, fire, and mechanical hazards.",
        "preview_url": "https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=13252_1",
        "preview_id": "13252_1"
    }
]

def seed_database():
    print("=== Starting BIS Standards Database Seed Process ===")
    
    # 1. Initialize with flagship standards
    print(f"Adding {len(FLAGSHIP_STANDARDS)} foundational Indian Standards across all key domains...")
    save_to_csv(FLAGSHIP_STANDARDS, CSV_FILE, append=False)
    
    # 2. Scrape live from standardsbis.bsbedge.com
    scraper = BISScraper()
    live_keywords = [
        "electrical energy",
        "transmission",
        "switchgear",
        "transformer",
        "water meter"
    ]
    
    for kw in live_keywords:
        print(f"\n[Scraping Live Portal] Keyword: '{kw}'...")
        try:
            items = scraper.scrape_and_enrich(kw, fetch_descriptions=True, max_items=6)
            if items:
                print(f"  Fetched {len(items)} standards for '{kw}'.")
                save_to_csv(items, CSV_FILE, append=True)
            else:
                print(f"  No items or connection timeout for '{kw}'.")
        except Exception as e:
            print(f"  Failed scraping '{kw}': {e}")
            
    print("\n=== Database Seeding Complete! ===")

if __name__ == "__main__":
    seed_database()

