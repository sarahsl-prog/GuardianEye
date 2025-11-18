#!/usr/bin/env python3
"""Script to seed the vector store with security knowledge."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.vector_store import initialize_vector_store, seed_security_knowledge


def main():
    """Seed the vector store."""
    print("🛡️ GuardianEye Vector Store Seeding")
    print("=" * 40)

    print("Initializing vector store...")
    initialize_vector_store()

    print("Seeding security knowledge...")
    seed_security_knowledge()

    print("✅ Vector store seeded successfully!")


if __name__ == "__main__":
    main()
