"""
Database Storage Layer (PostgreSQL with CSV fallback)
Allows permanent storage across production restarts, deployments, and ephemeral containers.
Works with Render PostgreSQL, Neon, Supabase, AWS RDS, or any PostgreSQL connection string.
Falls back seamlessly to local standards_data.csv if DATABASE_URL is not provided.
"""

import os
import csv
from typing import List, Dict, Any, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

CSV_DEFAULT_PATH = "standards_data.csv"

FIELDS = [
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

def get_database_url() -> Optional[str]:
    """Retrieves database connection string from environment."""
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

def init_db():
    """Initializes PostgreSQL table and seeds it with existing CSV data if empty."""
    db_url = get_database_url()
    if not db_url or not PSYCOPG2_AVAILABLE:
        return

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS standards (
                is_no VARCHAR(120) PRIMARY KEY,
                title TEXT,
                status VARCHAR(50),
                technical_committee VARCHAR(120),
                amendments VARCHAR(50),
                reaffirmed_year VARCHAR(50),
                price_in_india VARCHAR(50),
                price_outside_india VARCHAR(50),
                description TEXT,
                preview_url TEXT,
                preview_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM standards;")
        count = cur.fetchone()[0]
        
        if count == 0 and os.path.exists(CSV_DEFAULT_PATH):
            print(f"[Database] Seeding PostgreSQL from {CSV_DEFAULT_PATH}...")
            with open(CSV_DEFAULT_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                seed_rows = list(reader)
            
            insert_query = """
                INSERT INTO standards (
                    is_no, title, status, technical_committee, amendments,
                    reaffirmed_year, price_in_india, price_outside_india,
                    description, preview_url, preview_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (is_no) DO NOTHING;
            """
            
            for row in seed_rows:
                is_no = (row.get("is_no") or "").strip().upper()
                if not is_no:
                    continue
                cur.execute(insert_query, (
                    is_no,
                    row.get("title", ""),
                    row.get("status", "Active"),
                    row.get("technical_committee", ""),
                    str(row.get("amendments", "0")),
                    row.get("reaffirmed_year", ""),
                    row.get("price_in_india", ""),
                    row.get("price_outside_india", ""),
                    row.get("description", ""),
                    row.get("preview_url", ""),
                    row.get("preview_id", "")
                ))
            conn.commit()
            print(f"[Database] Seeded PostgreSQL successfully.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[Database] PostgreSQL initialization note: {e}")

def load_all_standards(csv_path: str = CSV_DEFAULT_PATH) -> List[Dict[str, Any]]:
    """
    Loads all standards records from PostgreSQL if DATABASE_URL is configured.
    Falls back gracefully to CSV.
    """
    db_url = get_database_url()
    if db_url and PSYCOPG2_AVAILABLE:
        try:
            conn = psycopg2.connect(db_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT is_no, title, status, technical_committee, amendments,
                       reaffirmed_year, price_in_india, price_outside_india,
                       description, preview_url, preview_id
                FROM standards
                ORDER BY created_at DESC, is_no ASC;
            """)
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"[Database] PostgreSQL query error, falling back to CSV: {e}")

    if not os.path.exists(csv_path):
        return []

    standards = []
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                standards.append(dict(row))
    except Exception as e:
        print(f"[Database] Error reading CSV: {e}")
    return standards

def save_standards(standards: List[Dict[str, Any]], csv_path: str = CSV_DEFAULT_PATH) -> int:
    """
    Saves standards to PostgreSQL (upsert) AND keeps local CSV in sync.
    Returns the count of newly inserted records.
    """
    newly_added = 0
    db_url = get_database_url()

    if db_url and PSYCOPG2_AVAILABLE:
        try:
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            upsert_query = """
                INSERT INTO standards (
                    is_no, title, status, technical_committee, amendments,
                    reaffirmed_year, price_in_india, price_outside_india,
                    description, preview_url, preview_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (is_no) DO UPDATE SET
                    title = EXCLUDED.title,
                    status = EXCLUDED.status,
                    technical_committee = EXCLUDED.technical_committee,
                    amendments = EXCLUDED.amendments,
                    price_in_india = EXCLUDED.price_in_india,
                    price_outside_india = EXCLUDED.price_outside_india,
                    description = COALESCE(NULLIF(EXCLUDED.description, ''), standards.description),
                    preview_url = COALESCE(NULLIF(EXCLUDED.preview_url, ''), standards.preview_url)
                RETURNING (xmax = 0);
            """

            for std in standards:
                is_no = (std.get("is_no") or "").strip().upper()
                if not is_no:
                    continue
                cur.execute(upsert_query, (
                    is_no,
                    std.get("title", ""),
                    std.get("status", "Active"),
                    std.get("technical_committee", ""),
                    str(std.get("amendments", "0")),
                    std.get("reaffirmed_year", ""),
                    std.get("price_in_india", ""),
                    std.get("price_outside_india", ""),
                    std.get("description", ""),
                    std.get("preview_url", ""),
                    std.get("preview_id", "")
                ))
                result = cur.fetchone()
                if result and result[0]:
                    newly_added += 1

            conn.commit()
            cur.close()
            conn.close()
            print(f"[Database] PostgreSQL upserted {len(standards)} item(s), new inserts: {newly_added}")
        except Exception as e:
            print(f"[Database] PostgreSQL save error: {e}")

    try:
        from scraper import save_to_csv
        csv_added = save_to_csv(standards, csv_path, append=True)
        if not db_url:
            newly_added = csv_added
    except Exception as e:
        print(f"[Database] Backup CSV save error: {e}")

    return newly_added