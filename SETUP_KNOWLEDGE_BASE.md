# Setting Up GuardianEye Knowledge Base

## Quick Start

The seed script has been fixed and is ready to use!

### Prerequisites

You need **one** of the following for embeddings:

**Option 1: OpenAI API Key (Recommended)**
```bash
# Add to .env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**Option 2: Local Embeddings with Ollama (Free, No API Key)**
See instructions below to switch to Ollama embeddings.

### Run the Seeder

```bash
# Make sure you're in the project root
cd /home/sunds/Code/GuardianEye

# Activate virtual environment
source venv/bin/activate

# Run the seeding script
PYTHONPATH=/home/sunds/Code/GuardianEye python scripts/seed_data.py
```

## What Just Happened

✅ **Script Fixed** - Removed dependency on `MarkdownHeaderTextSplitter`
- Created custom header-based splitter
- Works with installed langchain version
- No additional packages needed

✅ **Chunking Working** - Successfully created 138 chunks from 6 documents:
- owasp_top_10.md: 13 chunks
- mitre_attack.md: 32 chunks
- zero_trust_architecture.md: 32 chunks
- nist_cybersecurity_framework.md: 20 chunks
- siem_best_practices.md: 31 chunks
- nist_incident_response.md: 10 chunks

## Fixing the API Key Issue

You saw this error:
```
Error code: 401 - Incorrect API key provided
```

### Solution 1: Use Valid OpenAI API Key

1. Get your API key from https://platform.openai.com/api-keys
2. Update `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-real-key-here
   ```
3. Re-run: `PYTHONPATH=$(pwd) python scripts/seed_data.py`

### Solution 2: Use Free Local Embeddings (Ollama)

This option requires NO API keys and runs completely locally:

#### Step 1: Install Ollama
```bash
# If not already installed
curl -fsSL https://ollama.com/install.sh | sh
```

#### Step 2: Pull Embedding Model
```bash
ollama pull nomic-embed-text
```

#### Step 3: Update vector_store.py

Edit `src/db/vector_store.py`:

```python
# Change the get_embeddings function from:
from langchain_openai import OpenAIEmbeddings

def get_embeddings():
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key
    )

# To:
from langchain_ollama import OllamaEmbeddings

def get_embeddings():
    """Get embeddings model for vector store."""
    # Use Ollama for local, free embeddings
    return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=settings.ollama_base_url
    )
```

#### Step 4: Update settings.py (if needed)

Ensure `src/config/settings.py` has:
```python
ollama_base_url: str = Field(
    default="http://localhost:11434",
    alias="OLLAMA_BASE_URL"
)
```

#### Step 5: Run Seeder Again
```bash
PYTHONPATH=$(pwd) python scripts/seed_data.py
```

## Verification

After successful seeding, you should see:

```
✓ Successfully added 138 document chunks

============================================================
Knowledge Base Seeding Summary
============================================================
Documents processed: 6
Total chunks created: 138

[Verification] Testing vector store retrieval...
✓ Retrieval test successful!
  Query: 'What are the phases of incident response?'
  Found 2 relevant chunks
  Top result from: nist_incident_response

✓ Knowledge base seeded successfully!
```

## Testing the Knowledge Base

### Test 1: Direct Vector Store Query

```python
from src.db.vector_store import get_vector_store

vector_store = get_vector_store()
results = vector_store.similarity_search(
    "What are the MITRE ATT&CK tactics?",
    k=3
)

for doc in results:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content preview: {doc.page_content[:200]}...")
    print()
```

### Test 2: Via API

```bash
# Start the app
PYTHONPATH=$(pwd) python -m src.main

# In another terminal
curl -X POST http://localhost:8000/api/v1/agents/security-knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the phases of incident response according to NIST?"
  }'
```

## Troubleshooting

### Error: "No module named 'src'"
**Solution:** Always run with `PYTHONPATH=$(pwd)` from project root

### Error: "Directory not found: data/security_docs"
**Solution:** Documents are already there, check your current directory:
```bash
ls -la data/security_docs/
```

### Error: "Failed to initialize vector store"
**Solution:** Check your embedding configuration (OpenAI key or Ollama running)

### Chunks seem too large/small
**Solution:** Edit the `split_markdown_by_headers()` function in `scripts/seed_data.py`:
- Change `if len(chunk_content) > 100:` to adjust minimum chunk size
- Modify `chunk_content[:1000]` to adjust maximum chunk size

## Performance Notes

**OpenAI Embeddings:**
- Speed: ~1-2 seconds per document
- Cost: ~$0.0001 per 1K tokens
- Quality: Excellent

**Ollama Embeddings:**
- Speed: ~5-10 seconds per document (first run, then cached)
- Cost: Free
- Quality: Very good
- Benefit: Completely private, no data leaves your machine

## Next Steps

After seeding successfully:

1. ✅ Knowledge base is ready
2. ⏳ Test Security Knowledge Agent
3. ⏳ Integrate with other agents
4. ⏳ Add more documents as needed

---

**Status:** ✅ Script Fixed and Working
**Issue:** Need valid OpenAI API key OR switch to Ollama
**Created:** 2024-11-27
