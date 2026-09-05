"""
BIS Domain Knowledge Base
Covers BIS Certification Schemes, Licensing Procedures (Manakonline),
Hallmarking (HUID), Testing Laboratories, MSME concessions, and Consumer Rights.
"""

BIS_SCHEMES = {
    "Scheme-I (ISI Mark - Product Certification Scheme)": {
        "name": "Scheme-I (ISI Mark)",
        "type": "Mandatory & Voluntary Product Certification",
        "portal": "Manakonline (www.manakonline.in) -> e-BIS",
        "description": "The most recognized conformity mark in India. Involves factory inspection, assessment of in-house testing facilities, quality control personnel, independent sampling, and third-party laboratory testing before grant of license (CM/L number).",
        "applicable_sectors": [
            "Packaged drinking water (IS 14543)",
            "Mineral water (IS 13428)",
            "LPG cylinders & valves",
            "Infant milk foods & milk powders",
            "Cement & Clinker (IS 269, IS 1489)",
            "Structural & TMT Steel (IS 1786, IS 2062)",
            "Electrical cables & conductors (IS 694, IS 1554)",
            "Automotive helmets (IS 4151)",
            "Toys (IS 9873)",
            "Chemicals, fertilizers, and pressure cookers"
        ],
        "licensing_steps": [
            "Step 1: Ascertain the relevant Indian Standard (IS) and check whether it falls under a Mandatory Quality Control Order (QCO).",
            "Step 2: Ensure manufacturing unit has necessary manufacturing machinery and in-house testing equipment as per BIS Scheme of Inspection and Testing (SIT).",
            "Step 3: Register on Manakonline portal (www.manakonline.in) and submit application (Form-V) with required documents and application fee.",
            "Step 4: BIS Technical Officer conducts on-site factory audit, inspects quality control processes, and draws verification samples.",
            "Step 5: Samples tested in BIS Central/Regional Lab or BIS-recognized NABL laboratory.",
            "Step 6: Upon scrutiny of test report and audit compliance, BIS grants Certification Marks License (CM/L) allowing use of the ISI Mark."
        ],
        "msme_concessions": "50% concession on application fee, annual license fee, and marking fee for Micro enterprises, and 20% for Small enterprises. 50% concession for women entrepreneurs and startups."
    },
    "Scheme-II (CRS - Compulsory Registration Scheme)": {
        "name": "Scheme-II (CRS)",
        "type": "Self-Declaration of Conformity for Electronics & IT Goods",
        "portal": "CRS Portal (www.crsbis.in)",
        "description": "Introduced by Ministry of Electronics & IT (MeitY) and BIS. Does not require initial factory audit. Registration is granted based on testing of product samples in BIS-recognized labs followed by self-declaration of conformity.",
        "applicable_sectors": [
            "LED Lamps and Luminaires (IS 16102)",
            "Lithium-ion Batteries and Cells (IS 16046)",
            "Mobile phones, Laptops, Tablets, and Servers (IS 13252)",
            "Power adapters and chargers (IS 13252)",
            "Solar Photovoltaic Inverters and Modules (IS 14286, IS 16221)",
            "Smartwatches, Bluetooth speakers, and Smart cameras"
        ],
        "licensing_steps": [
            "Step 1: Submit product sample to a BIS-recognized Indian testing lab for testing against applicable IS.",
            "Step 2: Obtain valid test report (valid for 90 days from date of issue).",
            "Step 3: Register online on BIS CRS portal (www.crsbis.in) and submit test report along with Undertaking and documentation.",
            "Step 4: Scrutiny by BIS CRS branch and grant of Registration Number (R-XXXXXXXX).",
            "Step 5: Affix Standard Mark containing registration number and IS number on product and packaging."
        ],
        "msme_concessions": "Simplified fast-track digital approval within 15-20 working days."
    },
    "Scheme-IV (Certificate of Conformity - CoC)": {
        "name": "Scheme-IV (CoC)",
        "type": "Lot-wise / Batch-wise certification or specified goods",
        "portal": "Manakonline portal",
        "description": "Granted for specific batches or lots of products, or special categories where full factory licensing is not required.",
        "applicable_sectors": ["Special batch chemicals", "Pre-fabricated construction elements", "Import consignments"]
    },
    "FMCS (Foreign Manufacturers Certification Scheme)": {
        "name": "Foreign Manufacturers Certification Scheme (FMCS)",
        "type": "Overseas manufacturing units exporting to India",
        "portal": "Manakonline -> FMCS Division",
        "description": "Enables overseas factories to obtain BIS ISI Mark license to export goods covered under mandatory QCOs into India. Requires appointment of an Authorized Indian Representative (AIR) and physical audit of overseas facility by BIS inspectors.",
        "applicable_sectors": ["Steel, tires, automotive components, chemicals, electronics, toys manufactured outside India."]
    },
    "Hallmarking Scheme (Gold and Silver)": {
        "name": "BIS Hallmarking Scheme",
        "type": "Purity Certification of Precious Metals",
        "portal": "BIS e-HUID portal & BIS Care Mobile App",
        "description": "Mandatory certification of gold jewellery and artefacts in notified districts of India. Protects consumers against adulteration and under-karatage.",
        "standards": ["IS 1417 (Gold)", "IS 2112 (Silver)", "IS 15820 (Assaying & Hallmarking Centres)"],
        "three_hallmarks": [
            "1. BIS Logo (Triangle Manak symbol)",
            "2. Purity / Fineness Grade (e.g., 22K916 for 22 Karat / 91.6% purity, 18K750 for 18 Karat / 75.0% purity, 14K585 for 14 Karat)",
            "3. HUID (Hallmark Unique Identification) - A 6-digit alphanumeric laser code stamped on every individual jewellery piece."
        ],
        "consumer_verification": "Consumers can instantly verify the authenticity, jeweller registration, hallmarking centre, and article type using the 'Verify HUID' feature in the official BIS Care Mobile App."
    }
}

BIS_LABORATORIES = [
    {
        "name": "BIS Central Laboratory (CL)",
        "location": "Sahibabad, Ghaziabad, Uttar Pradesh",
        "capabilities": "Comprehensive testing of electrical products, electronics, chemicals, mechanical items, food, water, microbiology, and building materials."
    },
    {
        "name": "BIS Western Regional Laboratory (WRL)",
        "location": "Andheri East, Mumbai, Maharashtra",
        "capabilities": "Testing of plastics, packaging, consumer goods, food products, electrical cables, and metals."
    },
    {
        "name": "BIS Eastern Regional Laboratory (ERL)",
        "location": "Salt Lake, Kolkata, West Bengal",
        "capabilities": "Metallurgical testing, chemical testing, mechanical engineering products, civil and cement testing."
    },
    {
        "name": "BIS Southern Regional Laboratory (SRL)",
        "location": "CIT Campus, Taramani, Chennai, Tamil Nadu",
        "capabilities": "Electrical motors, pumps, electronics, chemicals, drinking water, and textile testing."
    },
    {
        "name": "BIS Northern Regional Laboratory (NRL)",
        "location": "Mohali / Chandigarh",
        "capabilities": "Food, agricultural products, chemicals, mechanical and electrical testing."
    },
    {
        "name": "BIS Recognized / NABL Accredited Private Labs",
        "location": "Pan-India (Over 300+ laboratories across all states)",
        "capabilities": "Authorized under BIS Laboratory Recognition Scheme (LRS) to test product samples under Scheme I, Scheme II (CRS), and QCO compliance."
    }
]

CONSUMER_SERVICES = {
    "BIS Care Mobile App": "Official mobile app available on Android & iOS for consumers to: (1) Verify ISI mark authenticity via CM/L license number, (2) Verify Gold Hallmarking HUID, (3) Verify CRS Registration number (R-number), (4) Register consumer complaints against defective certified products or misuse of ISI mark.",
    "National Consumer Helpline (NCH)": "Toll-free 1915 or portal consumerhelpline.gov.in for lodging complaints regarding unfair trade practices, sub-standard products, or un-hallmarked gold.",
    "Quality Control Orders (QCO)": "Mandatory orders issued by Government of India ministries (DoCA, DPIIT, MeitY, MoRTH, Steel, Textiles, Power) making BIS certification compulsory. Selling non-certified goods covered under QCO is a punishable offence with heavy fines, seizure of stock, and imprisonment under the BIS Act, 2016."
}

