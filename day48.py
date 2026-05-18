from cache import QueryCache
from tracker import RequestTracker
from logger import RequestLogger

print("CACHE + TRACKER + LOGGER TEST:")
print("=" * 55)

cache   = QueryCache(max_size=3)
tracker = RequestTracker()
logger  = RequestLogger()

# Test cache
print("\n1. CACHE TEST:")
cache.set("kidney dosage", "50% reduction required")
cache.set("side effects",  "nausea and headache")

result = cache.get("kidney dosage")
print(f"  Result: {result}")

result = cache.get("unknown query")
print(f"  Miss: {result}")

print(f"  Stats: {cache.stats()}")

# Test tracker
print("\n2. TRACKER TEST:")

tracker.record(
    "/analyze",
    "kidney dosage",
    "gpt-3.5-turbo",
    342,
    1850,
    True
)

tracker.record(
    "/compare",
    "compare docs",
    "gpt-4",
    891,
    4200,
    True
)

stats = tracker.stats()

print(f"  Total requests: {stats['total_requests']}")
print(f"  P50 latency:    {stats['p50_latency_ms']}ms")
print(f"  P95 latency:    {stats['p95_latency_ms']}ms")
print(f"  Total cost:     ${stats['total_cost_usd']}")

# Test logger
print("\n3. LOGGER TEST:")

logger.log(
    "INFO",
    "/analyze",
    "Request received",
    {"tokens": 342}
)

logger.log(
    "ERROR",
    "/compare",
    "LLM timeout",
    {"retry": 1}
)

# Day 48 — Quiz Answers

# Why does /compare use GPT-4 but /summarize uses GPT-3.5?

#Document comparison requires deeper reasoning and understanding differences across documents, so GPT-4 is used for higher quality. Summarization is simpler and GPT-3.5 is faster and much cheaper.

# What is the cache key format you used?

##The cache key format is:
#f"{question}:{doc_ids}"

#This uniquely identifies the question and document combination.

# What does P95 latency mean in plain English?

#P95 latency means 95% of requests complete faster than this value. It measures worst-case user experience more realistically than average latency.

# What would you change to use Redis instead of dictionary?

#Replace the in-memory dictionary with Redis get and set operations. Redis also adds persistence, expiration times, and sharing across multiple API servers.

# How does /upload handle multiple files simultaneously?

#The endpoint accepts a list of UploadFile objects and processes each PDF inside a loop, chunking and indexing each document independently.

# What happens if similarity score is below 0.3 in /analyze?

#The system returns:
#"Cannot find relevant information."

#This prevents hallucinated answers from weak retrieval results.

# What does the /stats endpoint return?

#It returns:
##- total requests
#- P50 latency
#- P95 latency
#- total tokens
#- total estimated cost
#- cache size
#- model usage statistics

## What is model routing in one sentence?

#Model routing selects different LLMs based on query complexity to balance quality, latency, and API cost.