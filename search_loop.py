"""
Automated Live Search-Scrape-Retrieve-DualLLM Loop
Takes any user input (keyword or IS number):
  1. Extracts the core search term or IS number.
  2. Searches live on standardsbis.bsbedge.com.
  3. Scrapes all matching webpage data (IS no, title, status, committee, amendments, prices).
  4. Fetches the backend HTML preview document (National Foreword, Scope, rule description).
  5. Saves / updates the data into standards_data.csv.
  6. Passes retrieved candidate records into LLM 1 (filter & extract exact facts).
  7. Passes LLM 1 findings into LLM 2 (conversational response with schemes, labs, licensing, MSME concessions).
  8. Returns the final answer to the user and is ready for the next loop iteration.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from scraper import BISScraper, save_to_csv
from retriever import StandardsRetriever
from llm_pipeline import DualLLMPipeline

class BISSearchLoop:
    def __init__(self, csv_file: str = "standards_data.csv"):
        self.csv_file = csv_file
        self.scraper = BISScraper()
        self.retriever = StandardsRetriever(csv_file)
        self.pipeline = DualLLMPipeline()

    def extract_search_keyword(self, user_query: str) -> Tuple[str, bool]:
        """
        Extracts search term and determines if it is a specific IS Number.
        Returns: (search_term, is_standard_number)
        """
        q = user_query.strip()

        # 1. Detect IS Number pattern (e.g., IS 138, IS:138, IS-138, IS138, IS 10500)
        is_match = re.search(r"\bIS\s*[:\-\s]?\s*(\d+)\b", q, flags=re.IGNORECASE)
        if is_match:
            std_num = is_match.group(1)
            return (f"IS {std_num}", True)

        # 2. Check if user typed a pure number query (e.g., '138' or 'standard 138')
        raw_num_match = re.search(r"\b(\d{2,5})\b", q)
        if raw_num_match and ("standard" in q.lower() or len(q.split()) <= 2):
            std_num = raw_num_match.group(1)
            return (f"IS {std_num}", True)

        # 3. Strip conversational filler phrases to isolate product/topic
        clean_q = re.sub(
            r"\b(what|is|the|standard|standards|for|in|and|or|a|an|to|how|can|do|i|get|of|with|which|are|bis|indian|license|licensing|certification|scheme|mandatory|tell|me|about|give|details|apply|applies|tested|testing|guidelines|requirement|requirements)\b",
            "",
            q,
            flags=re.IGNORECASE
        )
        tokens = [t for t in clean_q.split() if len(t) > 2]
        if tokens:
            return (" ".join(tokens[:3]), False)
        return (q, False)

    def execute_loop_iteration(
        self,
        user_query: str,
        language: str = "English",
        provider: str = "auto",
        custom_key: Optional[str] = None,
        max_scrape_items: int = 15,
        enable_live_scrape: bool = True
    ) -> Dict[str, Any]:
        """
        Executes one full pass of the loop for a user query.
        """
        search_term, is_standard_number = self.extract_search_keyword(user_query)
        scraped_items: List[Dict[str, Any]] = []
        newly_saved_count = 0
        target_url = ""

        # Step 1 & 2: Search webpage & scrape live data
        if enable_live_scrape and search_term:
            try:
                if is_standard_number:
                    target_url = f"https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?Standard_Number={search_term.replace(' ', '+')}&id=0"
                else:
                    target_url = f"https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?keyword={search_term.replace(' ', '+')}&id=0"

                # Scrape matching items from standardsbis.bsbedge.com
                scraped_items = self.scraper.scrape_and_enrich(
                    search_term,
                    is_standard_number=is_standard_number,
                    fetch_descriptions=True,
                    max_items=max_scrape_items
                )
                
                # Step 3: Save / update into CSV
                if scraped_items:
                    newly_saved_count = save_to_csv(scraped_items, self.csv_file, append=True)
            except Exception as e:
                print(f"[BISSearchLoop] Live scraping error for '{search_term}' (is_std={is_standard_number}): {e}")

        # Step 4: Refresh retriever and score candidate records from CSV
        self.retriever.load_data()
        scored_candidates = self.retriever.search(user_query, top_k=4)

        # If candidates are still empty (e.g. live scrape had no hits), fallback search on clean search_term
        if not scored_candidates and search_term != user_query:
            scored_candidates = self.retriever.search(search_term, top_k=4)

        candidates_text = self.retriever.format_candidates_for_llm(scored_candidates)

        # Step 5 & 6: Run Dual-LLM Pipeline (LLM 1 -> LLM 2)
        # Re-initialize clients to catch any changes in .env
        self.pipeline._init_clients()
        
        pipeline_result = self.pipeline.run(
            user_query=user_query,
            candidates_text=candidates_text,
            scored_items=scored_candidates,
            language=language,
            provider=provider,
            custom_key=custom_key
        )

        return {
            "user_query": user_query,
            "search_term": search_term,
            "is_standard_number": is_standard_number,
            "target_url": target_url,
            "scraped_count": len(scraped_items),
            "newly_saved_count": newly_saved_count,
            "scraped_items": scraped_items,
            "scored_candidates": scored_candidates,
            "candidates_text": candidates_text,
            "llm1_output": pipeline_result["llm1_output"],
            "llm2_output": pipeline_result["llm2_output"],
            "provider_used": pipeline_result["provider"],
            "language": language
        }

