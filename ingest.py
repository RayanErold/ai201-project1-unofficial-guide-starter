"""
ingest.py — Milestone 3: Document Ingestion & Chunking
Consumer Rights RAG System

Pipeline stage implemented here:
    [Raw .txt documents] -> [Cleaning] -> [Character chunking] -> [Chunks + metadata]

Reads the 10 source documents, normalizes their text, splits each into
overlapping fixed-size character chunks, and attaches provenance metadata to
every chunk so the retrieval stage (Milestone 4, ChromaDB) can cite sources.

Standard library only.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Resolve paths relative to this file so the script runs from any working dir.
DATA_DIR = Path(__file__).resolve().parent / "documents" / "data" / "raw"

CHUNK_SIZE = 500     # characters per chunk
CHUNK_OVERLAP = 100  # characters shared between consecutive chunks

# Source provenance, transcribed from the "Document Sources" table in README.md.
# `source` in each chunk's metadata is the filename (required by the spec); the
# issuing organization and canonical URL are carried alongside it so generated
# answers can surface a real citation. Values are flat strings because ChromaDB
# only accepts str/int/float/bool metadata.
SOURCE_METADATA = {
    "doc_1_credit_score_rights.txt": {
        "organization": "Consumer Financial Protection Bureau (CFPB)",
        "url": "https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/",
    },
    "doc_2_security_deposit_laws.txt": {
        "organization": "US Dept of Housing and Urban Development (HUD)",
        "url": "https://www.hud.gov/topics/rental_assistance/tenantrights",
    },
    "doc_3_airline_passenger_refunds.txt": {
        "organization": "US Department of Transportation (DOT)",
        "url": "https://www.transportation.gov/airconsumer/flights-and-rights",
    },
    "doc_4_medical_bill_protection.txt": {
        "organization": "Centers for Medicare & Medicaid Services (CMS)",
        "url": "https://www.cms.gov/nosurprises/consumers",
    },
    "doc_5_bank_overdraft_loopholes.txt": {
        "organization": "Consumer Financial Protection Bureau (CFPB)",
        "url": "https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/overdraft-services/",
    },
    "doc_6_student_loan_forgiveness.txt": {
        "organization": "Federal Student Aid (.gov)",
        "url": "https://studentaid.gov/manage-loans/forgiveness-cancellation",
    },
    "doc_7_subscription_cancel_laws.txt": {
        "organization": "Federal Trade Commission (FTC)",
        "url": "https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule",
    },
    "doc_8_credit_card_fraud_liability.txt": {
        "organization": "Federal Trade Commission (FTC)",
        "url": "https://www.consumer.ftc.gov/articles/lost-or-stolen-credit-atm-debit-cards",
    },
    "doc_9_car_lemon_laws.txt": {
        "organization": "USA.gov Official Portal",
        "url": "https://www.usa.gov/car-repair-recalled-lemon",
    },
    "doc_10_wage_theft_protections.txt": {
        "organization": "US Department of Labor (DOL)",
        "url": "https://www.dol.gov/agencies/whd/fact-sheets/16-flsa-deductions",
    },
}


# --------------------------------------------------------------------------- #
# Cleaning
# --------------------------------------------------------------------------- #

def clean_text(text: str) -> str:
    """Normalize whitespace and strip blank lines from raw document text.

    - Collapses runs of spaces/tabs within a line down to a single space.
    - Drops lines that are empty or whitespace-only.
    - Rejoins the surviving lines with a single newline.
    """
    cleaned_lines = []
    for line in text.splitlines():
        # Collapse internal whitespace runs (spaces, tabs) to one space.
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:  # skip blank / whitespace-only lines
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


# --------------------------------------------------------------------------- #
# Chunking
# --------------------------------------------------------------------------- #

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into fixed-size character chunks with a sliding-window overlap.

    Each chunk is up to ``chunk_size`` characters. Consecutive chunks share
    ``overlap`` characters so a legal clause split across a boundary still
    appears intact in at least one chunk. The window advances by
    ``chunk_size - overlap`` characters each step.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    text = text.strip()
    if not text:
        return []

    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]
        if chunk:
            chunks.append(chunk)
        # Stop once this chunk reaches the end of the text.
        if start + chunk_size >= len(text):
            break
    return chunks


# --------------------------------------------------------------------------- #
# Ingestion
# --------------------------------------------------------------------------- #

def build_chunks(data_dir: Path = DATA_DIR) -> list[dict]:
    """Read every .txt file in ``data_dir``, clean it, chunk it, and tag it.

    Returns a list of records shaped as::

        {"text": <chunk text>, "metadata": {"source": <filename>, ...}}

    Every chunk carries metadata identifying its parent source file.
    """
    if not data_dir.is_dir():
        sys.exit(f"ERROR: data directory not found: {data_dir}")

    files = sorted(data_dir.glob("*.txt"))
    if not files:
        sys.exit(f"ERROR: no .txt files found in {data_dir}")

    records: list[dict] = []
    for file_path in files:
        filename = file_path.name
        raw = file_path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)

        # Look up provenance; fall back gracefully if a file isn't in the table.
        provenance = SOURCE_METADATA.get(filename, {})

        for index, chunk in enumerate(chunks):
            metadata = {
                "source": filename,  # required: parent source file name
                "organization": provenance.get("organization", "Unknown"),
                "url": provenance.get("url", ""),
                "chunk_index": index,
            }
            records.append({"text": chunk, "metadata": metadata})

        print(f"  {filename}: {len(chunks)} chunks")

    return records


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

def main() -> None:
    print(f"Reading documents from: {DATA_DIR}\n")
    records = build_chunks()

    print("\n" + "=" * 70)
    print(f"TOTAL CHUNKS GENERATED: {len(records)}")
    print("=" * 70)

    sample_size = min(5, len(records))
    print(f"\nRandom sample of {sample_size} chunk(s):\n")
    for i, record in enumerate(random.sample(records, sample_size), start=1):
        print(f"--- Sample {i} ---")
        print(f"Metadata: {record['metadata']}")
        print(f"Text ({len(record['text'])} chars): {record['text']!r}")
        print()


if __name__ == "__main__":
    main()
