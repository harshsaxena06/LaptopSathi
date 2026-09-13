"""
End-to-end Knowledge Base update pipeline (CLI).
Run:
    python scripts/run_ingestion.py --file data/raw/laptops_raw.csv
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db
from app.admin.kb_admin import run_ingestion_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("laptopsathi.run_ingestion")


def main():
    parser = argparse.ArgumentParser(description="Run the full LaptopSathi ingestion pipeline")
    parser.add_argument("--file", required=True, help="Path to raw CSV/JSON file")
    parser.add_argument("--notes", default="", help="Optional notes for this KB version")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        result = run_ingestion_pipeline(db, args.file, notes=args.notes)
        logger.info("Knowledge base updated: version=%s records=%d", result["version_tag"], result["record_count"])
        logger.info("Next: run `python scripts/build_embeddings.py` to refresh semantic search.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
