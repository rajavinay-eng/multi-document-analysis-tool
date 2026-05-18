# Multi-Document Analysis Tool

Upload multiple PDFs. Ask questions across all documents.
Compare documents. Track costs. Monitor latency.

## Live API
http://YOUR_EC2_IP:8000/docs

## Architecture
Multiple PDFs → Parse → Chunk (400 tokens)
→ Embed → ChromaDB (with doc_id metadata)
→ Hybrid Search (BM25 + Semantic)
→ CrossEncoder Reranking
→ Model Routing (GPT-3.5 vs GPT-4)
→ LLM Generation
→ Cost Tracking + Latency Monitoring

## Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /health | GET | System status |
| /upload | POST | Upload multiple PDFs |
| /analyze | POST | Cross-document Q&A |
| /compare | POST | Compare two documents |
| /summarize | POST | Summarize document |
| /stats | GET | Cost + latency metrics |

## Key Features
- Multi-document support with doc_id metadata
- Model routing: GPT-3.5 for simple, GPT-4 for complex
- Cost tracking per request
- P50 + P95 latency monitoring
- Query result caching (Redis-ready)
- Rate limiting: 20 requests/minute per IP
- Full request logging
- GitHub Actions CI/CD

## Tech Stack
FastAPI · ChromaDB · sentence-transformers
CrossEncoder · LangChain · Docker · AWS EC2
GitHub Actions · tiktoken · PyMuPDF

## Setup
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

## Design Decisions
GPT-4 only for /compare — 15x cost of GPT-3.5
Caching avoids repeated LLM calls for same query
P95 tracks worst-case user experience
Hybrid search handles both meaning and exact terms
