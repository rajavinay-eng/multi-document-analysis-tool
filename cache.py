# day48.py — Piece 1 — Supporting modules

import time
import statistics
from collections import defaultdict
from datetime import datetime
import json

# ══════════════════════════════════════════════
# cache.py — Query caching
# ══════════════════════════════════════════════

class QueryCache:
    """
    In-memory query cache.
    Redis awareness: in production replace
    self._cache dict with Redis client.

    Redis version would be:
      import redis
      r = redis.Redis(host='localhost', port=6379)
      r.setex(key, 3600, value)  # expire in 1 hour
      r.get(key)
    """
    def __init__(self, max_size=100):
        self._cache   = {}
        self._max     = max_size
        self._hits    = 0
        self._misses  = 0

    def get(self, key):
        if key in self._cache:
            self._hits += 1
            print(f"  [cache HIT] {key[:40]}")
            return self._cache[key]
        self._misses += 1
        return None

    def set(self, key, value):
        if len(self._cache) >= self._max:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value

    def stats(self):
        total = self._hits + self._misses
        rate  = self._hits/total if total > 0 else 0
        return {
            "hits":      self._hits,
            "misses":    self._misses,
            "hit_rate":  round(rate, 3),
            "cached":    len(self._cache)
        }

