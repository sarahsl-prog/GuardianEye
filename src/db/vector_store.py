"""Chroma vector store for RAG capabilities."""

import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config.settings import settings


_vector_store: Optional[Chroma] = None


def get_embeddings():
    """Get embeddings model for vector store.

    Supports multiple embedding providers with automatic fallback:
    - Ollama (free, local, no API key required)
    - OpenAI (cloud-based, requires API key)

    Returns:
        Embeddings model instance
    """
    # Check for embedding provider preference in environment
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()

    if embedding_provider == "ollama":
        try:
            from langchain_ollama import OllamaEmbeddings

            print("Using Ollama embeddings (local, free)")
            return OllamaEmbeddings(
                model="nomic-embed-text",
                base_url=settings.ollama_base_url
            )
        except ImportError:
            print("⚠ langchain-ollama not installed, falling back to OpenAI")
            embedding_provider = "openai"
        except Exception as e:
            print(f"⚠ Ollama embeddings failed: {e}")
            print("  Falling back to OpenAI embeddings")
            embedding_provider = "openai"

    if embedding_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        print("Using OpenAI embeddings")
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key
        )

    raise ValueError(f"Unsupported embedding provider: {embedding_provider}")


def initialize_vector_store(persist_directory: Optional[str] = None) -> Chroma:
    """Initialize the Chroma vector store.

    Args:
        persist_directory: Directory to persist the vector store

    Returns:
        Initialized Chroma vector store
    """
    global _vector_store

    persist_dir = persist_directory or settings.chroma_persist_directory

    # Create directory if it doesn't exist
    os.makedirs(persist_dir, exist_ok=True)

    # Initialize embeddings
    embeddings = get_embeddings()

    # Create or load vector store
    _vector_store = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name="guardianeye_knowledge"
    )

    return _vector_store


def get_vector_store() -> Chroma:
    """Get the vector store instance.

    Returns:
        Chroma vector store instance

    Raises:
        RuntimeError: If vector store not initialized
    """
    global _vector_store

    if _vector_store is None:
        _vector_store = initialize_vector_store()

    return _vector_store


async def add_documents(documents: list[Document]) -> list[str]:
    """Add documents to the vector store.

    Args:
        documents: List of documents to add

    Returns:
        List of document IDs
    """
    vector_store = get_vector_store()
    return vector_store.add_documents(documents)


async def search_similar(query: str, k: int = 3) -> list[Document]:
    """Search for similar documents.

    Args:
        query: Search query
        k: Number of results to return

    Returns:
        List of similar documents
    """
    vector_store = get_vector_store()
    return vector_store.similarity_search(query, k=k)


def seed_security_knowledge():
    """Seed the vector store with security knowledge documents."""
    documents = [
        Document(
            page_content="NIST Cybersecurity Framework consists of five core functions: Identify, Protect, Detect, Respond, and Recover. It provides a policy framework of computer security guidance for how organizations can assess and improve their ability to prevent, detect, and respond to cyber attacks.",
            metadata={"source": "NIST CSF", "category": "framework"}
        ),
        Document(
            page_content="The OWASP Top 10 is a standard awareness document for web application security. It represents a broad consensus about the most critical security risks to web applications. Current top risks include Injection, Broken Authentication, Sensitive Data Exposure, XML External Entities (XXE), Broken Access Control, Security Misconfiguration, Cross-Site Scripting (XSS), Insecure Deserialization, Using Components with Known Vulnerabilities, and Insufficient Logging & Monitoring.",
            metadata={"source": "OWASP", "category": "vulnerabilities"}
        ),
        Document(
            page_content="Incident Response Process typically follows these phases: 1) Preparation - establishing incident response capabilities, 2) Detection & Analysis - identifying and analyzing security incidents, 3) Containment, Eradication & Recovery - stopping the incident and restoring systems, 4) Post-Incident Activity - lessons learned and improvements.",
            metadata={"source": "NIST SP 800-61", "category": "incident_response"}
        ),
        Document(
            page_content="Zero Trust Architecture is based on the principle of 'never trust, always verify'. It assumes no implicit trust is granted to assets or user accounts based solely on their physical or network location. Key principles include: verify explicitly, use least privilege access, and assume breach.",
            metadata={"source": "NIST SP 800-207", "category": "architecture"}
        ),
        Document(
            page_content="MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. It provides a common taxonomy of adversary behavior organized into tactics (what adversaries are trying to achieve) and techniques (how they achieve it).",
            metadata={"source": "MITRE", "category": "threat_intelligence"}
        ),
        Document(
            page_content="Security Information and Event Management (SIEM) systems provide real-time analysis of security alerts generated by applications and network hardware. Key capabilities include: log aggregation, correlation, alerting, dashboards, compliance reporting, and forensic analysis.",
            metadata={"source": "Security Best Practices", "category": "tools"}
        ),
        Document(
            page_content="Vulnerability Management Lifecycle: 1) Discovery - identify assets and vulnerabilities, 2) Prioritization - assess risk and business impact, 3) Remediation - apply patches or mitigations, 4) Verification - confirm fixes are effective. CVSS scoring helps prioritize based on severity.",
            metadata={"source": "Security Operations", "category": "vulnerability_management"}
        ),
        Document(
            page_content="Defense in Depth strategy employs multiple layers of security controls. If one layer fails, others continue to provide protection. Layers include: perimeter security, network security, host security, application security, and data security.",
            metadata={"source": "Security Architecture", "category": "defense_strategy"}
        ),
    ]

    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    print(f"Seeded {len(documents)} security knowledge documents to vector store")
