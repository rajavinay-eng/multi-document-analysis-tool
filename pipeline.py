# Piece 2 — pipeline.py

import chromadb
import numpy as np
import time
import os
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from langchain_core.prompts import PromptTemplate
import tiktoken

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
reranker    = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
enc         = tiktoken.encoding_for_model("gpt-3.5-turbo")
client      = chromadb.PersistentClient(path="./project3_db")
collection  = client.get_or_create_collection(
    name="multi_docs",
    metadata={"hnsw:space": "cosine"}
)

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a document analyst.
Answer ONLY from the provided context.
If not found: 'I cannot find this information.'
Always cite source document and page.

Context:
{context}

Question: {question}

Answer:"""
)

def normalize(s):
    a = np.array(s)
    if a.max() == a.min():
        return np.zeros_like(a)
    return (a - a.min()) / (a.max() - a.min())

def route_model(query_type):
    """Model routing — use GPT-4 only when needed"""
    expensive = ["compare", "analyze_complex", "contrast"]
    return "gpt-4" if query_type in expensive else "gpt-3.5-turbo"

def hybrid_search(query, doc_id=None, n=8):
    """Hybrid BM25 + semantic — from Project 2"""
    if collection.count() == 0:
        return []

    q_emb  = embed_model.encode([query])
    params = {
        "query_embeddings": q_emb.tolist(),
        "n_results":        min(n, collection.count()),
        "include":          ["documents","metadatas","distances"]
    }
    if doc_id:
        params["where"] = {"doc_id": doc_id}

    results = collection.query(**params)
    docs    = results["documents"][0]
    metas   = results["metadatas"][0]
    dists   = results["distances"][0]

    if not docs:
        return []

    tokenized   = [d.lower().split() for d in docs]
    bm25        = BM25Okapi(tokenized)
    bm25_norm   = normalize(bm25.get_scores(query.lower().split()))
    sem_norm    = normalize(np.array([1-d for d in dists]))
    combined    = 0.5 * sem_norm + 0.5 * bm25_norm
    top_idx     = np.argsort(combined)[::-1]

    return [{
        "text":       docs[i],
        "doc_id":     metas[i].get("doc_id",""),
        "doc_name":   metas[i].get("doc_name","Doc"),
        "page":       metas[i].get("page", 1),
        "similarity": round(float(combined[i]), 3)
    } for i in top_idx]

def rerank(query, candidates, n=3):
    """CrossEncoder reranking"""
    if not candidates:
        return []
    pairs  = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates),
                    reverse=True, key=lambda x: x[0])
    top    = [c for _, c in ranked[:n]]
    for i, (sc, _) in enumerate(ranked[:n]):
        top[i]["rerank_score"] = round(float(sc), 3)
    return top

def call_llm(prompt, model="gpt-3.5-turbo"):
    """LLM call with token counting"""
    tokens = len(enc.encode(prompt)) + 150
    api_key = os.getenv("OPENAI_API_KEY", "")

    if api_key:
        from openai import OpenAI
        llm    = OpenAI(api_key=api_key)
        resp   = llm.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            temperature=0.1, max_tokens=500
        )
        answer = resp.choices[0].message.content
        tokens = resp.usage.total_tokens
    else:
        answer = f"[Demo mode — set OPENAI_API_KEY] Context received."

    return answer, tokens

def run_rag(question, doc_id=None, query_type="search"):
    """Complete RAG pipeline"""
    start      = time.time()
    model      = route_model(query_type)
    candidates = hybrid_search(question, doc_id=doc_id)

    if not candidates:
        return {
            "answer":  "No documents indexed.",
            "sources": [], "tokens": 0,
            "model": model,
            "latency_ms": round((time.time()-start)*1000, 1)
        }

    if candidates[0]["similarity"] < 0.3:
        return {
            "answer":  "Cannot find relevant information.",
            "sources": [], "tokens": 0,
            "model": model,
            "latency_ms": round((time.time()-start)*1000, 1)
        }

    top     = rerank(question, candidates)
    context = "\n\n".join([
        f"[{c['doc_name']}, p.{c['page']}]\n{c['text']}"
        for c in top
    ])
    prompt  = PROMPT.format(context=context, question=question)
    answer, tokens = call_llm(prompt, model)

    return {
        "answer":     answer,
        "sources":    top,
        "tokens":     tokens,
        "model":      model,
        "latency_ms": round((time.time()-start)*1000, 1)
    }

# Test
print("\nPIPELINE TEST:")
print("=" * 50)
print(f"Model for 'compare':  {route_model('compare')}")
print(f"Model for 'search':   {route_model('search')}")
print(f"Model for 'summarize': {route_model('summarize')}")
result = run_rag("What is the dosage for kidney patients?")
print(f"\nRAG test:")
print(f"  Model:   {result['model']}")
print(f"  Tokens:  {result['tokens']}")
print(f"  Latency: {result['latency_ms']}ms")
print(f"  Answer:  {result['answer'][:80]}")