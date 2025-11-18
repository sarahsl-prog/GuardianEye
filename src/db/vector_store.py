"""Vector store utilities using Chroma."""

import chromadb
from chromadb.config import Settings

from src.config.settings import settings as app_settings


def get_chroma_client():
    """
    Create Chroma client for vector storage.

    Returns:
        Chroma client instance
    """
    client = chromadb.Client(Settings(
        persist_directory=app_settings.chroma_persist_directory,
        anonymized_telemetry=False
    ))
    return client


def get_or_create_collection(client, collection_name: str = "guardianeye"):
    """
    Get or create a Chroma collection.

    Args:
        client: Chroma client
        collection_name: Name of the collection

    Returns:
        Chroma collection
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "GuardianEye knowledge base"}
    )
    return collection
