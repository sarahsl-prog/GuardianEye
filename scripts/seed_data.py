"""Seed test data for development."""

import asyncio
import re
from pathlib import Path
from langchain_core.documents import Document

from src.db.vector_store import add_documents, initialize_vector_store, get_vector_store
from src.config.settings import settings


def categorize_document(filename: str) -> str:
    """Categorize document by filename for metadata."""
    categories = {
        "nist_incident_response": "incident_response",
        "nist_cybersecurity_framework": "compliance",
        "owasp_top_10": "vulnerability_management",
        "mitre_attack": "threat_intelligence",
        "zero_trust_architecture": "architecture",
        "siem_best_practices": "operations",
    }
    return categories.get(filename, "general")


def extract_framework(filename: str) -> str:
    """Extract framework name from filename."""
    if "nist" in filename:
        return "NIST"
    elif "owasp" in filename:
        return "OWASP"
    elif "mitre" in filename:
        return "MITRE"
    else:
        return "Industry Standards"


def split_markdown_by_headers(content: str, source_name: str) -> list[Document]:
    """
    Split markdown content by headers (H1, H2, H3).

    This is a simple implementation to replace MarkdownHeaderTextSplitter.
    It splits on headers and preserves context.
    """
    chunks = []

    # Split by major headers (## and ###)
    # Pattern: split on lines starting with ## or ###
    sections = re.split(r'\n(?=##)', content)

    current_title = ""
    current_section = ""

    for section in sections:
        if not section.strip():
            continue

        # Extract header levels
        lines = section.split('\n')
        first_line = lines[0] if lines else ""

        # Determine header level and text
        if first_line.startswith('###'):
            subsection = first_line.replace('###', '').strip()
            chunk_content = '\n'.join(lines[1:]).strip()

            if len(chunk_content) > 100:  # Only create chunk if substantial
                doc = Document(
                    page_content=chunk_content,
                    metadata={
                        "source": source_name,
                        "file_type": "markdown",
                        "category": categorize_document(source_name),
                        "framework": extract_framework(source_name),
                        "title": current_title,
                        "section": current_section,
                        "subsection": subsection,
                        "topics": f"{current_section}, {subsection}" if current_section else subsection,
                    }
                )
                chunks.append(doc)

        elif first_line.startswith('##'):
            current_section = first_line.replace('##', '').strip()
            chunk_content = '\n'.join(lines[1:]).strip()

            if len(chunk_content) > 100:  # Only create chunk if substantial
                doc = Document(
                    page_content=chunk_content,
                    metadata={
                        "source": source_name,
                        "file_type": "markdown",
                        "category": categorize_document(source_name),
                        "framework": extract_framework(source_name),
                        "title": current_title,
                        "section": current_section,
                        "subsection": "",
                        "topics": current_section,
                    }
                )
                chunks.append(doc)

        elif first_line.startswith('#'):
            current_title = first_line.replace('#', '').strip()
            chunk_content = '\n'.join(lines[1:]).strip()

            # For H1, include some intro content if available
            if len(chunk_content) > 100:
                doc = Document(
                    page_content=chunk_content[:1000],  # Limit intro chunk
                    metadata={
                        "source": source_name,
                        "file_type": "markdown",
                        "category": categorize_document(source_name),
                        "framework": extract_framework(source_name),
                        "title": current_title,
                        "section": "Overview",
                        "subsection": "",
                        "topics": current_title,
                    }
                )
                chunks.append(doc)

    # If no chunks created, add the whole document as one chunk
    if not chunks and content.strip():
        doc = Document(
            page_content=content,
            metadata={
                "source": source_name,
                "file_type": "markdown",
                "category": categorize_document(source_name),
                "framework": extract_framework(source_name),
                "title": source_name.replace('_', ' ').title(),
                "section": "Full Document",
                "subsection": "",
                "topics": source_name.replace('_', ' '),
            }
        )
        chunks.append(doc)

    return chunks


async def seed_knowledge_base():
    """Seed knowledge base with security documents from data/security_docs."""
    print("\n" + "=" * 60)
    print("Seeding Security Knowledge Base")
    print("=" * 60)

    # Initialize vector store
    print("\n[1/4] Initializing vector store...")
    try:
        initialize_vector_store()
        print("✓ Vector store initialized")
    except Exception as e:
        print(f"✗ Failed to initialize vector store: {e}")
        return

    # Load security documents
    print("\n[2/4] Loading security documents...")
    docs_dir = Path("data/security_docs")

    if not docs_dir.exists():
        print(f"✗ Directory not found: {docs_dir}")
        print("  Please ensure security documents are in data/security_docs/")
        return

    # Count markdown files (excluding README)
    md_files = [f for f in docs_dir.glob("*.md") if f.name != "README.md"]
    print(f"  Found {len(md_files)} security documents")

    # Set up markdown chunking by headers
    print("\n[3/4] Chunking documents by headers...")

    all_chunks = []
    doc_stats = {}

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into semantic chunks using simple header-based splitting
            chunks = split_markdown_by_headers(content, md_file.stem)

            all_chunks.extend(chunks)
            doc_stats[md_file.name] = len(chunks)
            print(f"  ✓ {md_file.name}: {len(chunks)} chunks")

        except Exception as e:
            print(f"  ✗ Error processing {md_file.name}: {e}")

    # Add all chunks to vector store
    print(f"\n[4/4] Adding {len(all_chunks)} chunks to vector store...")
    try:
        await add_documents(all_chunks)
        print(f"✓ Successfully added {len(all_chunks)} document chunks")
    except Exception as e:
        print(f"✗ Failed to add documents to vector store: {e}")
        print(f"  Error details: {str(e)}")
        return

    # Verify the seeding
    print("\n" + "=" * 60)
    print("Knowledge Base Seeding Summary")
    print("=" * 60)
    print(f"Documents processed: {len(md_files)}")
    print(f"Total chunks created: {len(all_chunks)}")
    print("\nChunks per document:")
    for doc_name, chunk_count in doc_stats.items():
        print(f"  - {doc_name}: {chunk_count} chunks")

    # Test retrieval
    print("\n[Verification] Testing vector store retrieval...")
    try:
        vector_store = get_vector_store()
        test_query = "What are the phases of incident response?"
        results = vector_store.similarity_search(test_query, k=2)

        if results:
            print(f"✓ Retrieval test successful!")
            print(f"  Query: '{test_query}'")
            print(f"  Found {len(results)} relevant chunks")
            print(f"  Top result from: {results[0].metadata.get('source', 'unknown')}")
        else:
            print("⚠ Retrieval test returned no results")
    except Exception as e:
        print(f"⚠ Retrieval test failed: {e}")

    print("\n✓ Knowledge base seeded successfully!")


async def seed_users():
    """Seed test users for development."""
    print("\n" + "=" * 60)
    print("Seeding Test Users")
    print("=" * 60)

    # Note: This will be implemented when database models are created
    # For now, we'll create a placeholder

    print("\n⚠ User seeding not yet implemented")
    print("  Waiting for database models (src/db/models.py) to be implemented")
    print("  Once models are ready, this will seed:")
    print("    - Admin user (admin/admin)")
    print("    - Demo analyst user (analyst/analyst)")
    print("    - Demo viewer user (viewer/viewer)")

    # TODO: Implement user seeding once models are ready
    # Example implementation:
    """
    from src.db.models import User
    from src.db.postgres import get_postgres_connection
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    users = [
        {
            "username": "admin",
            "email": "admin@guardianeye.local",
            "password": pwd_context.hash("admin"),
            "role": "admin",
            "is_active": True,
        },
        {
            "username": "analyst",
            "email": "analyst@guardianeye.local",
            "password": pwd_context.hash("analyst"),
            "role": "analyst",
            "is_active": True,
        },
        {
            "username": "viewer",
            "email": "viewer@guardianeye.local",
            "password": pwd_context.hash("viewer"),
            "role": "viewer",
            "is_active": True,
        },
    ]

    async with get_postgres_connection().begin() as conn:
        for user_data in users:
            # Insert user into database
            await conn.execute(User.__table__.insert().values(**user_data))
            print(f"  ✓ Created user: {user_data['username']}")
    """

    print("\n⏳ User seeding skipped (not implemented)")


async def seed_sample_incidents():
    """Seed sample security incidents for testing (future enhancement)."""
    print("\n" + "=" * 60)
    print("Sample Incidents")
    print("=" * 60)
    print("\n⚠ Sample incident seeding not yet implemented")
    print("  Future enhancement: Add sample security incidents for testing")
    print("  Will include:")
    print("    - Brute force attack scenarios")
    print("    - Malware detection incidents")
    print("    - Data exfiltration attempts")
    print("    - Privilege escalation cases")
    print("\n⏳ Incident seeding skipped (not implemented)")


async def main():
    """Main seeding function."""
    print("\n" + "=" * 70)
    print(" " * 20 + "GuardianEye Data Seeding")
    print("=" * 70)
    print(f"\nEnvironment: {settings.app_env}")
    print(f"Vector Store: {settings.chroma_persist_directory}")

    try:
        # Seed knowledge base
        await seed_knowledge_base()

        # Seed users (placeholder for now)
        await seed_users()

        # Seed sample incidents (future)
        await seed_sample_incidents()

    except Exception as e:
        print(f"\n✗ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 70)
    print("✓ Data seeding completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Start the application: python -m src.main")
    print("2. Test the Security Knowledge Agent at /api/v1/agents/security-knowledge")
    print("3. Try queries like: 'What are the NIST incident response phases?'")
    print()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
