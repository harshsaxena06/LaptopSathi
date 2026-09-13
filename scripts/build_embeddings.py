"""
Builds/rebuilds the FAISS semantic-search index from all active laptops in
the knowledge database. Run this after every `run_ingestion.py` update.

Run:
    python scripts/build_embeddings.py
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.search import semantic_search

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("laptopsathi.build_embeddings")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        count = semantic_search.build_index(db)
        logger.info("Semantic search index ready with %d vectors.", count)
    finally:
        db.close()
