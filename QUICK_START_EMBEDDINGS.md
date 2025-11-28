# Quick Start: Setting Up Embeddings for GuardianEye

## ✅ Changes Made

The vector store now supports **automatic provider selection** with fallback:

1. **Ollama embeddings** (default) - Free, local, no API key
2. **OpenAI embeddings** (fallback) - Cloud-based, requires API key

## 🚀 Option 1: Use Ollama (Recommended - Free & Local)

### Step 1: Install Ollama

```bash
# Install Ollama if not already installed
curl -fsSL https://ollama.com/install.sh | sh

# Or check if already installed
ollama --version
```

### Step 2: Pull Embedding Model

```bash
# Download the embedding model (one-time, ~270MB)
ollama pull nomic-embed-text
```

### Step 3: Configure Environment

Add to your `.env` file (or it will use ollama by default):

```bash
# Optional - this is the default
EMBEDDING_PROVIDER=ollama
```

### Step 4: Run the Seeder

```bash
./seed.sh
```

Expected output:
```
Using Ollama embeddings (local, free)
✓ Vector store initialized
✓ Successfully added 138 document chunks
```

**That's it!** No API keys needed, completely free and private.

---

## 🌐 Option 2: Use OpenAI Embeddings

If you prefer OpenAI or Ollama isn't available:

### Step 1: Get OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

### Step 2: Configure Environment

Edit `.env`:

```bash
# Switch to OpenAI embeddings
EMBEDDING_PROVIDER=openai

# Add your API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Model (optional - this is default)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Step 3: Run the Seeder

```bash
./seed.sh
```

Expected output:
```
Using OpenAI embeddings
✓ Vector store initialized
✓ Successfully added 138 document chunks
```

**Cost:** ~$0.01 for seeding all documents (very cheap!)

---

## 🔄 Automatic Fallback

The system automatically falls back to OpenAI if Ollama fails:

```bash
# If Ollama is configured but not running:
⚠ Ollama embeddings failed: connection refused
  Falling back to OpenAI embeddings
Using OpenAI embeddings
```

---

## ✅ Testing Your Setup

### Quick Test

```bash
# Run the seeder
./seed.sh
```

Look for these success indicators:
- ✅ `Using Ollama embeddings (local, free)` OR `Using OpenAI embeddings`
- ✅ `✓ Vector store initialized`
- ✅ `✓ Successfully added 138 document chunks`
- ✅ `✓ Retrieval test successful!`

### Verify Data

```python
# Test retrieval
from src.db.vector_store import get_vector_store

vector_store = get_vector_store()
results = vector_store.similarity_search(
    "What are the NIST incident response phases?",
    k=3
)

print(f"Found {len(results)} results")
for doc in results:
    print(f"- {doc.metadata['source']}: {doc.page_content[:100]}...")
```

---

## 📊 Comparison: Ollama vs OpenAI

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| **Cost** | Free | ~$0.01 to seed |
| **Privacy** | 100% local | Cloud-based |
| **Speed** | Fast (local) | Fast (API) |
| **Quality** | Excellent | Excellent |
| **Setup** | One command | API key needed |
| **Dependencies** | Ollama service | Internet + API key |

**Recommendation:** Use Ollama for development and testing. Both work equally well!

---

## 🛠️ Troubleshooting

### "Connection refused" when using Ollama

**Solution 1:** Start Ollama service
```bash
# Check if Ollama is running
ollama list

# If not, it will auto-start on next command
ollama serve
```

**Solution 2:** Let it fallback to OpenAI
```bash
# Just add your OpenAI key to .env
OPENAI_API_KEY=sk-...
```

### "Invalid API key" with OpenAI

**Check your key:**
```bash
# Verify key in .env is correct
grep OPENAI_API_KEY .env

# Test the key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Model not found (Ollama)

```bash
# Pull the embedding model
ollama pull nomic-embed-text

# Verify it's available
ollama list | grep nomic
```

### Want to use a different Ollama model?

Edit `src/db/vector_store.py`:

```python
return OllamaEmbeddings(
    model="mxbai-embed-large",  # Or any other embedding model
    base_url=settings.ollama_base_url
)
```

Available models:
- `nomic-embed-text` (recommended, 137M params)
- `mxbai-embed-large` (334M params, more accurate)
- `all-minilm` (smaller, faster)

---

## 🎯 Next Steps

After successful seeding:

1. ✅ **Knowledge base is ready** with 138 chunks from 6 security documents
2. 🚀 **Start the application:**
   ```bash
   PYTHONPATH=$(pwd) python -m src.main
   ```

3. 🧪 **Test the Security Knowledge Agent:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/agents/security-knowledge \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the NIST incident response phases?"}'
   ```

4. 📚 **Add more documents** to `data/security_docs/` and re-run seeder

---

## 📝 Summary

**What was changed:**
- ✅ `src/db/vector_store.py` - Now supports Ollama and OpenAI with auto-fallback
- ✅ `.env.example` - Added `EMBEDDING_PROVIDER` configuration
- ✅ Default set to Ollama (free, local, no API key)

**To use it:**
1. Run `ollama pull nomic-embed-text` (one-time setup)
2. Run `./seed.sh`
3. Done!

**Alternatively:**
1. Set `EMBEDDING_PROVIDER=openai` in `.env`
2. Add your `OPENAI_API_KEY`
3. Run `./seed.sh`

Both options work perfectly! 🎉
