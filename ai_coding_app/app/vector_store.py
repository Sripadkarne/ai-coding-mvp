import os
import csv
from typing import Optional

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Persist Chroma DB in a stable local folder inside the Django project
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
COLLECTION_NAME = "icd10_g_codes"

_vectorstore: Optional[Chroma] = None

def _build_vectorstore() -> Chroma:
    """
    Build a Chroma vector store from data/g_codes.csv and persist it locally.
    """
    # IMPORTANT: requires OPENAI_API_KEY in env
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Create/load collection
    vs = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )

    # If already populated, don't rebuild
    try:
        if vs._collection.count() > 0:
            return vs
    except Exception:
        # If count fails for any reason, fall through and rebuild
        pass

    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "g_codes.csv")

    docs = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            long_desc = (row.get("long_description") or "").strip()
            if not long_desc:
                continue

            docs.append(
                Document(
                    page_content=long_desc,
                    metadata={
                        "icd_code": (row.get("icd_code") or "").strip(),
                        "short_description": (row.get("short_description") or "").strip(),
                        "order_number": row.get("order_number"),
                        "valid_for_transaction": row.get("valid_for_transaction"),
                    },
                )
            )

    # Add all documents and persist
    vs.add_documents(docs)
    return vs


def get_vectorstore() -> Chroma:
    """
    Load or lazily initialize the persisted Chroma vector store
    containing ICD-10 G-code embeddings.

    :return: Initialized Chroma vector store.
    :rtype: Chroma
    """
    global _vectorstore
    if _vectorstore is None:
        os.makedirs(CHROMA_DIR, exist_ok=True)
        _vectorstore = _build_vectorstore()
    return _vectorstore
