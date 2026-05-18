# Piece 3 — main.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
import os
import tempfile
import fitz
import tiktoken
from collections import defaultdict

app = FastAPI(
    title="Multi-Document Analysis Tool",
    description="Project 3 — AI Engineer Portfolio",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])

# Initialize modules
enc           = tiktoken.encoding_for_model("gpt-3.5-turbo")
rate_limits   = defaultdict(list)

# Inline cache and tracker for demo
_cache    = {}
_requests = []

# ── REQUEST MODELS ────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    question:   str
    doc_ids:    Optional[List[str]] = None
    query_type: str = "search"

class CompareRequest(BaseModel):
    question: str
    doc_id_a: str
    doc_id_b: str

class SummarizeRequest(BaseModel):
    doc_id: str

# ── RATE LIMITER ──────────────────────────────────────────
def rate_limit(ip, limit=20, window=60):
    now   = time.time()
    times = [t for t in rate_limits[ip] if now-t < window]
    rate_limits[ip] = times
    if len(times) >= limit:
        raise HTTPException(429, f"Rate limit: {limit}/min")
    rate_limits[ip].append(now)

# ── MIDDLEWARE ────────────────────────────────────────────
@app.middleware("http")
async def latency_header(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    elapsed  = round((time.time()-start)*1000, 1)
    response.headers["X-Response-Time"] = f"{elapsed}ms"
    return response

# ── ENDPOINT 1: HEALTH ────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status":    "healthy",
        "timestamp": time.time(),
        "version":   "1.0.0"
    }

# ── ENDPOINT 2: UPLOAD ────────────────────────────────────
@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    """Upload multiple PDFs and index all"""
    results = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append({
                "filename": file.filename,
                "status":   "error",
                "message":  "Only PDF accepted"
            })
            continue

        contents = await file.read()
        doc_id   = file.filename.replace(".pdf","").replace(" ","_")
        start    = time.time()
        n_chunks = 0

        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            # Process PDF
            doc = fitz.open(tmp_path)
            chunks = []
            idx    = 0

            for page_num, page in enumerate(doc):
                text = page.get_text().strip()
                if not text:
                    continue
                tokens = enc.encode(text)
                for i in range(0, len(tokens), 350):
                    chunk_tok = tokens[i:i+400]
                    if not chunk_tok:
                        break
                    chunks.append({
                        "text":  enc.decode(chunk_tok),
                        "page":  page_num + 1,
                        "idx":   idx
                    })
                    idx += 1
                    if i + 400 >= len(tokens):
                        break
            doc.close()

            # Index to ChromaDB
            if chunks:
                from sentence_transformers import SentenceTransformer
                import chromadb
                em  = SentenceTransformer('all-MiniLM-L6-v2')
                cl  = chromadb.PersistentClient(path="./project3_db")
                col = cl.get_or_create_collection(
                    name="multi_docs",
                    metadata={"hnsw:space": "cosine"}
                )
                try:
                    col.delete(where={"doc_id": doc_id})
                except:
                    pass

                texts  = [c["text"] for c in chunks]
                embs   = em.encode(texts)
                metas  = [{"doc_id": doc_id,
                            "doc_name": file.filename,
                            "page": c["page"],
                            "chunk_idx": c["idx"]}
                           for c in chunks]
                ids    = [f"{doc_id}_c{c['idx']}" for c in chunks]
                col.add(documents=texts, embeddings=embs.tolist(),
                        metadatas=metas, ids=ids)
                n_chunks = len(chunks)

        finally:
            os.unlink(tmp_path)

        results.append({
            "filename":    file.filename,
            "doc_id":      doc_id,
            "status":      "success",
            "chunks":      n_chunks,
            "process_ms":  round((time.time()-start)*1000, 1)
        })

    return {"uploaded": len(results), "results": results}

# ── ENDPOINT 3: ANALYZE ───────────────────────────────────
@app.post("/analyze")
async def analyze(request: Request, body: AnalyzeRequest):
    """Cross-document Q&A with cost tracking"""
    rate_limit(request.client.host)

    if not body.question.strip():
        raise HTTPException(400, "Empty question")

    # Check cache
    cache_key = f"{body.question}:{body.doc_ids}"
    if cache_key in _cache:
        cached = _cache[cache_key]
        cached["cached"] = True
        return JSONResponse(content=cached)

    from pipeline import run_rag
    start  = time.time()
    result = run_rag(
        body.question,
        query_type=body.query_type
    )

    response = {
        "question":   body.question,
        "answer":     result["answer"],
        "sources":    result["sources"],
        "model":      result["model"],
        "tokens":     result["tokens"],
        "latency_ms": round((time.time()-start)*1000, 1),
        "cached":     False
    }

    _cache[cache_key] = response
    _requests.append({
        "endpoint":   "/analyze",
        "latency_ms": response["latency_ms"],
        "tokens":     result["tokens"],
        "model":      result["model"],
        "success":    True
    })

    return JSONResponse(content=response)

# ── ENDPOINT 4: COMPARE ───────────────────────────────────
@app.post("/compare")
async def compare(request: Request, body: CompareRequest):
    """Compare two documents — uses GPT-4"""
    rate_limit(request.client.host)

    from pipeline import hybrid_search, rerank, call_llm
    start = time.time()

    chunks_a = hybrid_search(body.question, doc_id=body.doc_id_a, n=4)
    chunks_b = hybrid_search(body.question, doc_id=body.doc_id_b, n=4)

    if not chunks_a and not chunks_b:
        raise HTTPException(404, "Documents not found")

    context_a = "\n".join([c["text"] for c in chunks_a[:2]])
    context_b = "\n".join([c["text"] for c in chunks_b[:2]])

    prompt = f"""Compare these two documents on: {body.question}

Document A ({body.doc_id_a}):
{context_a}

Document B ({body.doc_id_b}):
{context_b}

Provide structured comparison with key differences:"""

    answer, tokens = call_llm(prompt, model="gpt-4")

    return {
        "question":   body.question,
        "doc_a":      body.doc_id_a,
        "doc_b":      body.doc_id_b,
        "comparison": answer,
        "model":      "gpt-4",
        "tokens":     tokens,
        "latency_ms": round((time.time()-start)*1000, 1)
    }

# ── ENDPOINT 5: SUMMARIZE ─────────────────────────────────
@app.post("/summarize")
async def summarize(request: Request, body: SummarizeRequest):
    """Summarize one document — uses GPT-3.5"""
    rate_limit(request.client.host)

    cache_key = f"summary:{body.doc_id}"
    if cache_key in _cache:
        return JSONResponse(content={**_cache[cache_key],
                                      "cached": True})

    from pipeline import hybrid_search, call_llm
    start    = time.time()
    chunks   = hybrid_search("main topics and key points",
                              doc_id=body.doc_id, n=5)

    if not chunks:
        raise HTTPException(404, f"Document not found: {body.doc_id}")

    context = "\n\n".join([c["text"] for c in chunks[:3]])
    prompt  = f"""Summarize this document concisely in 3-5 sentences.
Focus on main topics and key findings.

Document content:
{context}

Summary:"""

    answer, tokens = call_llm(prompt, model="gpt-3.5-turbo")
    result = {
        "doc_id":     body.doc_id,
        "summary":    answer,
        "model":      "gpt-3.5-turbo",
        "tokens":     tokens,
        "latency_ms": round((time.time()-start)*1000, 1),
        "cached":     False
    }

    _cache[cache_key] = result
    return JSONResponse(content=result)

# ── ENDPOINT 6: STATS ─────────────────────────────────────
@app.get("/stats")
async def stats():
    """Usage statistics — cost, latency, requests"""
    import statistics as st

    if not _requests:
        return {"message": "No requests yet",
                "cache_size": len(_cache)}

    total     = len(_requests)
    latencies = [r["latency_ms"] for r in _requests]
    tokens    = [r["tokens"] for r in _requests]

    RATES = {"gpt-3.5-turbo": 0.002/1000, "gpt-4": 0.03/1000}
    total_cost = sum(
        r["tokens"] * RATES.get(r["model"], 0.002/1000)
        for r in _requests
    )

    return {
        "total_requests":  total,
        "p50_latency_ms":  round(st.median(latencies), 1),
        "p95_latency_ms":  round(
            sorted(latencies)[int(total*0.95)], 1
        ),
        "total_tokens":    sum(tokens),
        "total_cost_usd":  round(total_cost, 4),
        "cache_size":      len(_cache),
        "cost_note":       "Verify at platform.openai.com/pricing",
        "model_usage": {
            "gpt-3.5-turbo": sum(
                1 for r in _requests if r["model"]=="gpt-3.5-turbo"
            ),
            "gpt-4": sum(
                1 for r in _requests if r["model"]=="gpt-4"
            )
        }
    }

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("MAIN.PY — 6 ENDPOINTS:")
print("  GET  /health    — system status")
print("  POST /upload    — multiple PDF upload")
print("  POST /analyze   — cross-document Q&A")
print("  POST /compare   — compare two documents")
print("  POST /summarize — summarize one document")
print("  GET  /stats     — cost + latency metrics")