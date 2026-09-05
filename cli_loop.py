"""
Interactive CLI Loop for BIS AI Assistant
Repeatedly accepts user keywords or IS numbers in a loop:
  1. Searches live on standardsbis.bsbedge.com
  2. Scrapes webpage data + preview HTML doc
  3. Updates standards_data.csv
  4. Runs LLM 1 (filter & extract exact data)
  5. Runs LLM 2 (conversational response)
  6. Prints output and loops for the next input.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from search_loop import BISSearchLoop

def main():
    print("=" * 70)
    print("BIS AI Assistant - Continuous Search & Scrape Loop")
    print("Smart India Hackathon | Problem Statement ID: 26107")
    print("Type 'exit' or 'quit' to terminate the loop.")
    print("=" * 70)

    loop = BISSearchLoop()

    while True:
        try:
            print("\n" + "-" * 70)
            user_input = input("Enter Keyword or IS Number (e.g., 'pressure cooker', 'IS 1885', 'solar'): ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting BIS Assistant Loop. Goodbye!")
                break

            print(f"\n[1/4] Searching BIS Portal...")
            result = loop.execute_loop_iteration(user_input, language="English", max_scrape_items=5)
            print(f"       Target URL: {result.get('target_url')}")
            print(f"[2/4] Scraped {result['scraped_count']} standard(s) from webpage.")
            print(f"[3/4] Saved {result['newly_saved_count']} new record(s) to 'standards_data.csv'.")
            
            print("\n" + "=" * 35 + " [STAGE 1: LLM 1 OUTPUT] " + "=" * 35)
            print(result["llm1_output"])

            print("\n" + "=" * 35 + " [STAGE 2: LLM 2 OUTPUT] " + "=" * 35)
            print(result["llm2_output"])

        except KeyboardInterrupt:
            print("\nLoop interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"Error during loop iteration: {e}")

if __name__ == "__main__":
    main()

