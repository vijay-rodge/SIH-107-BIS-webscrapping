"""
Standards Retriever Module
Matches user queries against standards_data.csv using IS Number detection,
keyword matching, and relevance ranking to supply candidate context for LLM 1.
"""

import os
import re
import csv
from typing import List, Dict, Any, Tuple

DEFAULT_CSV_PATH = "standards_data.csv"

class StandardsRetriever:
    def __init__(self, csv_path: str = DEFAULT_CSV_PATH):
        self.csv_path = csv_path
        self.standards: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self):
        """Loads and refreshes standards from the CSV file."""
        if not os.path.exists(self.csv_path):
            self.standards = []
            return

        standards = []
        try:
            with open(self.csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    standards.append(row)
            self.standards = standards
        except Exception as e:
            print(f"[StandardsRetriever] Error loading CSV: {e}")
            self.standards = []

    def extract_is_numbers(self, query: str) -> List[str]:
        """Extracts candidate IS numbers from user query, e.g., IS 10500, IS:1417, 1885."""
        patterns = [
            r"\bIS\s*:?\s*(\d+)\b",
            r"\b(\d{3,5})\b"
        ]
        numbers = []
        for pat in patterns:
            matches = re.findall(pat, query, flags=re.IGNORECASE)
            for m in matches:
                if m not in numbers:
                    numbers.append(m)
        return numbers

    def score_standard(self, std: Dict[str, Any], query: str, is_nums: List[str]) -> float:
        """Calculates relevance score between query and standard record."""
        score = 0.0
        q_lower = query.lower()
        query_tokens = set(re.findall(r"\w+", q_lower))
        
        # Stop words to downweight
        stop_words = {"what", "is", "the", "standard", "for", "in", "and", "or", "a", "an", "to", "how", "can", "do", "i", "get", "of", "with", "which", "are", "bis", "indian"}
        meaningful_tokens = [t for t in query_tokens if t not in stop_words and len(t) > 2]

        is_no = std.get("is_no", "").lower()
        title = std.get("title", "").lower()
        desc = std.get("description", "").lower()
        tc = std.get("technical_committee", "").lower()

        # 1. Direct IS number match (Huge boost)
        for num in is_nums:
            if num in is_no:
                score += 50.0
            if num in desc:
                score += 15.0

        # 2. Token overlap in title (High boost)
        for token in meaningful_tokens:
            if token in title:
                score += 8.0
            if token in is_no:
                score += 10.0
            if token in desc:
                score += 3.0
            if token in tc:
                score += 4.0

        # 3. Exact phrase matching in title or description
        if len(meaningful_tokens) >= 2:
            phrase = " ".join(meaningful_tokens)
            if phrase in title:
                score += 25.0
            elif phrase in desc:
                score += 12.0

        # 4. Active status slight preference over withdrawn
        if std.get("status", "").lower() == "active":
            score += 1.0

        return score

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches standards CSV and returns top_k ranked records with scores.
        """
        self.load_data()  # dynamic reload to catch freshly scraped entries
        if not self.standards:
            return []

        is_nums = self.extract_is_numbers(query)
        scored_items = []

        for std in self.standards:
            score = self.score_standard(std, query, is_nums)
            if score > 0:
                scored_items.append((std, score))

        scored_items.sort(key=lambda x: x[1], reverse=True)
        return scored_items[:top_k]

    def format_candidates_for_llm(self, scored_items: List[Tuple[Dict[str, Any], float]]) -> str:
        """
        Formats candidate standards into structured text for LLM 1 prompt ingestion.
        """
        if not scored_items:
            return "No directly matching candidate standards found in current CSV knowledge base."

        formatted_blocks = []
        for i, (std, score) in enumerate(scored_items, 1):
            block = (
                f"Candidate {i} (Match Score: {score:.1f}):\n"
                f"  - IS Number: {std.get('is_no', 'N/A')}\n"
                f"  - Title: {std.get('title', 'N/A')}\n"
                f"  - Status: {std.get('status', 'N/A')}\n"
                f"  - Technical Committee: {std.get('technical_committee', 'N/A')}\n"
                f"  - Reaffirmed Year: {std.get('reaffirmed_year', 'N/A')}\n"
                f"  - Amendments: {std.get('amendments', '0')}\n"
                f"  - Price in India: {std.get('price_in_india', 'N/A')} | Outside: {std.get('price_outside_india', 'N/A')}\n"
                f"  - Rule Description / Scope (from Preview Doc): {std.get('description', 'N/A')}\n"
                f"  - BIS Preview Link: {std.get('preview_url', 'N/A')}\n"
            )
            formatted_blocks.append(block)

        return "\n".join(formatted_blocks)

