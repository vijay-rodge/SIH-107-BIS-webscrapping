"""
BIS Web Scraper & Preview Extractor
Targets standardsbis.bsbedge.com to search Indian Standards,
extract metadata, parse preview HTML documents for scope and description,
and store the structured records in a CSV dataset.
"""

import os
import re
import csv
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

BASE_SEARCH_URL = "https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx"
BASE_PREVIEW_URL = "https://standardsbis.bsbedge.com/"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

class BISScraper:
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def search_standards(self, query: str, is_standard_number: bool = False, timeout: int = 25) -> List[Dict[str, Any]]:
        """
        Scrapes standards search results from BIS portal.
        If is_standard_number is True:
          Uses https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?Standard_Number={query}&id=0
        Else:
          Uses https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?keyword={query}&id=0
        """
        if is_standard_number:
            params = {
                "Standard_Number": query,
                "id": "0"
            }
        else:
            params = {
                "keyword": query,
                "id": "0"
            }
        try:
            response = self.session.get(BASE_SEARCH_URL, params=params, timeout=timeout)
            response.raise_for_status()
        except Exception as e:
            print(f"[BISScraper] Error fetching search results for '{query}' (is_std={is_standard_number}): {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        panels = soup.find_all(lambda tag: tag.name == "div" and tag.get("id") and "Panel2" in tag.get("id"))
        
        standards = []
        for panel in panels:
            # 1. Standard Number
            std_no_el = panel.find(id=lambda x: x and "lblstdno" in x)
            if not std_no_el:
                continue
            is_no = std_no_el.get_text(strip=True)

            # 2. Reaffirmed year
            reaff_el = panel.find(id=lambda x: x and "lblreaff" in x and "lblreaff1" not in x and "lblreaff2" not in x)
            reaffirmed_year = reaff_el.get_text(strip=True) if reaff_el else ""

            # 3. Status
            status_el = panel.find(id=lambda x: x and "lblstatus" in x)
            status = status_el.get_text(strip=True) if status_el else "Active"

            # 4. Amendments
            amds_el = panel.find(id=lambda x: x and "noanmds" in x)
            amendments = amds_el.get_text(strip=True) if amds_el else "0"

            # 5. Price within India
            price_in_el = panel.find(id=lambda x: x and "lblINRPrice" in x)
            price_in = price_in_el.get_text(strip=True) if price_in_el else "N/A"

            # 6. Price outside India
            price_out_el = panel.find(id=lambda x: x and "lblUSDPrice" in x)
            price_out = price_out_el.get_text(strip=True) if price_out_el else "N/A"

            # 7. Preview URL & ID
            preview_a = panel.find("a", href=lambda x: x and "BIS_Preview.aspx" in x)
            preview_url = ""
            preview_id = ""
            if preview_a and preview_a.get("href"):
                href = preview_a["href"]
                preview_url = BASE_PREVIEW_URL + href if not href.startswith("http") else href
                if "id=" in href:
                    preview_id = href.split("id=")[-1]

            # 8. Technical Committee
            committee = ""
            tc_span = panel.find(lambda tag: tag.name == "span" and "Technical Committee" in tag.get_text())
            if tc_span and tc_span.next_sibling:
                raw_tc = str(tc_span.next_sibling).strip()
                committee = re.sub(r"\s+", " ", raw_tc)

            # 9. Title
            title = ""
            title_span = panel.find(lambda tag: tag.name == "span" and "font-size: 15px" in (tag.get("style") or ""))
            if title_span:
                title = title_span.get_text(strip=True)
            else:
                # Fallback: search spans in div-abc1
                div_abc1 = panel.find("div", class_="div-abc1")
                if div_abc1:
                    for s in div_abc1.find_all("span"):
                        txt = s.get_text(strip=True)
                        if txt and txt != is_no and "Reaffirmed" not in txt and "Technical" not in txt:
                            title = txt
                            break

            standards.append({
                "is_no": is_no,
                "title": title,
                "reaffirmed_year": reaffirmed_year,
                "status": status,
                "technical_committee": committee,
                "amendments": amendments,
                "price_in_india": price_in,
                "price_outside_india": price_out,
                "preview_url": preview_url,
                "preview_id": preview_id,
                "description": ""  # populated via fetch_preview_description
            })

        return standards

    def fetch_preview_description(self, preview_url: str, timeout: int = 15) -> str:
        """
        Fetches the preview HTML document from BIS_Preview.aspx and extracts
        the National Foreword, Scope, and rule description.
        """
        if not preview_url:
            return ""
        try:
            r = self.session.get(preview_url, timeout=timeout)
            if r.status_code != 200:
                return ""
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Extract meaningful text blocks
            body = soup.find("body")
            if not body:
                return ""
            
            paragraphs = []
            for p in body.find_all(["p", "div"]):
                txt = p.get_text(separator=" ", strip=True)
                # Filter out navigation or generic boilerplate
                if len(txt) > 25 and not any(skip in txt for skip in ["e-Sale Preview Standards", "Bureau of Indian Standards", "JavaScript"]):
                    if txt not in paragraphs:
                        paragraphs.append(txt)
            
            # Join paragraphs cleanly
            full_desc = " | ".join(paragraphs[:8])
            # Normalize whitespace
            full_desc = re.sub(r"\s+", " ", full_desc).strip()
            return full_desc
        except Exception as e:
            print(f"[BISScraper] Error fetching preview {preview_url}: {e}")
            return ""

    def scrape_and_enrich(self, query: str, is_standard_number: bool = False, fetch_descriptions: bool = True, max_items: int = 20) -> List[Dict[str, Any]]:
        """
        Scrapes standards for a query (keyword or IS Number) and enriches them with preview descriptions.
        """
        items = self.search_standards(query, is_standard_number=is_standard_number)
        if max_items:
            items = items[:max_items]

        if fetch_descriptions:
            for item in items:
                if item.get("preview_url"):
                    item["description"] = self.fetch_preview_description(item["preview_url"])
                    time.sleep(0.3)  # Polite crawling delay
        return items

def save_to_csv(standards: List[Dict[str, Any]], filepath: str, append: bool = True):
    """
    Saves or appends standards to a CSV file, avoiding duplicates by is_no.
    """
    fieldnames = [
        "is_no",
        "title",
        "status",
        "technical_committee",
        "amendments",
        "reaffirmed_year",
        "price_in_india",
        "price_outside_india",
        "description",
        "preview_url",
        "preview_id"
    ]

    existing_is_nos = set()
    file_exists = os.path.exists(filepath)

    if file_exists:
        try:
            with open(filepath, mode="r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("is_no"):
                        existing_is_nos.add(row["is_no"].strip().upper())
        except Exception as e:
            print(f"Error reading existing CSV: {e}")

    mode = "a" if (append and file_exists) else "w"
    added_count = 0

    with open(filepath, mode=mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists or not append:
            writer.writeheader()

        for std in standards:
            key = std.get("is_no", "").strip().upper()
            if not key or (append and key in existing_is_nos):
                continue
            
            row = {fn: std.get(fn, "") for fn in fieldnames}
            writer.writerow(row)
            existing_is_nos.add(key)
            added_count += 1

    print(f"[BISScraper] Saved {added_count} new standard(s) to '{filepath}'. Total unique: {len(existing_is_nos)}")
    return added_count

