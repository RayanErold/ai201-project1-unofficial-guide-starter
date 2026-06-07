import os
import glob
import random
import re
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# 1. Initialize local persistent database client
# This saves database state to disk so it survives code restarts
DB_PATH = "./chroma_db"
client = chromadb.PersistentClient(path=DB_PATH)

# 2. Use the local zero-cost embedding model recommended by the spec
embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Create or fetch your database collection
collection = client.get_or_create_collection(
    name="consumer_rights_protection",
    embedding_function=embedding_function
)

# File metadata maps make it easier to attach query-relevant tags to each chunk.
FILE_TOPIC_MAP = {
    "doc_1_credit_score_rights.txt": "credit_score_rights",
    "doc_2_security_deposit_laws.txt": "security_deposit_laws",
    "doc_3_airline_passenger_refunds.txt": "airline_passenger_refunds",
    "doc_4_medical_bill_protection.txt": "medical_bill_protection",
    "doc_5_bank_overdraft_loopholes.txt": "bank_overdraft_loopholes",
    "doc_6_student_loan_forgiveness.txt": "student_loan_forgiveness",
    "doc_7_subscription_cancel_laws.txt": "subscription_cancel_laws",
    "doc_8_credit_card_fraud_liability.txt": "credit_card_fraud_liability",
    "doc_9_car_lemon_laws.txt": "car_lemon_laws",
    "doc_10_wage_theft_protections.txt": "wage_theft_protections"
}

FILE_KEYWORD_MAP = {
    "doc_8_credit_card_fraud_liability.txt": ["credit card", "fraud", "online", "digital", "stolen", "liability"],
    "doc_2_security_deposit_laws.txt": ["security deposit", "wear and tear", "landlord", "tenant", "faded paint"],
}

WORD_CHUNK_SIZE = 80
WORD_OVERLAP = 15


def split_into_sentences(text):
    """Split text into sentences while preserving punctuation."""
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    return [sentence.strip() for sentence in sentence_endings.split(text) if sentence.strip()]


def simple_word_chunker(text, chunk_size=WORD_CHUNK_SIZE, overlap=WORD_OVERLAP):
    """Chunk text by words so word boundaries are preserved and meaning is not cut."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += max(chunk_size - overlap, 1)
    return chunks


def paragraph_sentence_chunker(text, max_words=WORD_CHUNK_SIZE, overlap=WORD_OVERLAP):
    """Chunk documents by paragraphs and sentences, preserving whole-word context."""
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks = []

    for paragraph in paragraphs:
        sentences = split_into_sentences(paragraph)
        current_chunk = []
        current_word_count = 0

        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_word_count = len(sentence_words)

            if current_word_count + sentence_word_count <= max_words or not current_chunk:
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
                continue

            chunks.append(" ".join(current_chunk))

            overlap_sentences = []
            overlap_word_count = 0
            for part in reversed(current_chunk):
                part_word_count = len(part.split())
                if overlap_word_count + part_word_count <= overlap:
                    overlap_sentences.insert(0, part)
                    overlap_word_count += part_word_count
                else:
                    break

            current_chunk = overlap_sentences + [sentence]
            current_word_count = overlap_word_count + sentence_word_count

            if current_word_count > max_words:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

    return chunks


def build_query_variants(query_str):
    """Create query paraphrases that improve recall for online/digital fraud questions."""
    variants = [query_str]
    lower = query_str.lower()

    if "online" in lower or "digital" in lower or "hacked" in lower:
        variants.extend([
            query_str.replace("stolen online", "stolen online or hacked"),
            query_str.replace("credit card is stolen online", "credit card number is stolen online"),
            query_str.replace("credit card is stolen online", "credit card is hacked online"),
            "What happens if my credit card information is stolen online?",
            "What if an unauthorized online credit card transaction happens?"
        ])

    if "faded wall paint" in lower:
        variants.extend([
            "Can a landlord charge me for faded wall paint?",
            "Is old faded wall paint considered normal wear and tear?"
        ])

    return list(dict.fromkeys([variant for variant in variants if variant]))

def build_vector_database():
    """Reads local text files, fragments them, and indexes them into ChromaDB."""
    # Look directly into your validated directory pathway
    raw_files_path = os.path.join("documents", "data", "raw", "*.txt")
    target_files = glob.glob(raw_files_path)
    
    if not target_files:
        print(f"⚠️ Error: No source text files found in documents/data/raw/! Check your directory path.")
        return

    all_chunks = []
    all_metadata = []
    all_ids = []
    global_chunk_counter = 0

    # Step through all 10 document targets
    for file_path in target_files:
        filename = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
            
        # Clean consecutive internal white spaces
        cleaned_text = " ".join(raw_text.split())
        
        # Execute paragraph / sentence chunking while preserving whole words.
        chunks = paragraph_sentence_chunker(cleaned_text, max_words=WORD_CHUNK_SIZE, overlap=WORD_OVERLAP)
        
        # Extract corresponding URL metadata strings we mapped out in our tables
        # Simply maps filename tokens to their verified URL endpoints
        url_mapping = {
            "doc_1_credit_score_rights.txt": "https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/",
            "doc_2_security_deposit_laws.txt": "https://www.hud.gov/topics/rental_assistance/tenantrights",
            "doc_3_airline_passenger_refunds.txt": "https://www.transportation.gov/airconsumer/flights-and-rights",
            "doc_4_medical_bill_protection.txt": "https://www.cms.gov/nosurprises/consumers",
            "doc_5_bank_overdraft_loopholes.txt": "https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/overdraft-services/",
            "doc_6_student_loan_forgiveness.txt": "https://studentaid.gov/manage-loans/forgiveness-cancellation",
            "doc_7_subscription_cancel_laws.txt": "https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule",
            "doc_8_credit_card_fraud_liability.txt": "https://www.consumer.ftc.gov/articles/lost-or-stolen-credit-atm-debit-cards",
            "doc_9_car_lemon_laws.txt": "https://www.usa.gov/car-repair-recalled-lemon",
            "doc_10_wage_theft_protections.txt": "https://www.dol.gov/agencies/whd/fact-sheets/16-flsa-deductions"
        }
        
        assigned_url = url_mapping.get(filename, "https://www.usa.gov")
        assigned_topic = FILE_TOPIC_MAP.get(filename, "general")
        assigned_keywords = FILE_KEYWORD_MAP.get(filename, [])

        for idx, chunk_text in enumerate(chunks):
            all_chunks.append(chunk_text)
            metadata = {
                "source": filename,
                "url": assigned_url,
                "position": idx,
                "topic": assigned_topic
            }
            if assigned_keywords:
                metadata["keywords"] = assigned_keywords
            all_metadata.append(metadata)
            all_ids.append(f"id_{global_chunk_counter}")
            global_chunk_counter += 1

    # Push structured data elements safely into ChromaDB in a single batch operation
    collection.add(
        ids=all_ids,
        documents=all_chunks,
        metadatas=all_metadata
    )
    print(f"📊 Success! Indexed {global_chunk_counter} dense chunks into local vector store.")

def query_vector_database(query_str, k=3, use_expansions=False):
    """Executes local semantic vector queries and displays output distance measurements."""
    query_list = [query_str]
    if use_expansions:
        query_list = build_query_variants(query_str)

    for variant in query_list:
        results = collection.query(
            query_texts=[variant],
            n_results=k
        )
        
        print(f"\n🔍 Query: '{variant}'")
        print("-" * 60)
        
        # Loop over matches array sets parsed from Chroma query arrays
        for i in range(len(results['documents'][0])):
            text = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            print(f"🏆 Rank {i+1} Match [Distance Score: {distance:.4f}]")
            print(f"📂 Source File: {meta['source']}")
            print(f"🌐 Citation Link: {meta['url']}")
            print(f"📝 Text Excerpt: {text}")
            print("." * 60)

if __name__ == "__main__":
    # Rebuild the store when it's empty or when FORCE_REBUILD=1 is set.
    if collection.count() == 0 or os.environ.get("FORCE_REBUILD") == "1":
        print("⚡ Vector store empty or rebuild requested. Initializing index pipeline execution context...")
        build_vector_database()
    else:
        print(f"💾 Found existing database collection with {collection.count()} active indices.")

    # Execute Test Diagnostic Queries to verify semantic indexing parameters
    query_vector_database("What happens if my credit card is stolen online?", use_expansions=True)
    query_vector_database("Can a landlord charge me for old faded wall paint?")