# ══════════════════════════════════════════════
# tracker.py — Cost and latency tracking
# ══════════════════════════════════════════════
import statistics
from datetime import datetime
class RequestTracker:
    """
    Tracks cost and latency for every request.
    In production: persist to database.
    For portfolio: in-memory is fine.
    """

    # Model pricing per 1000 tokens
    # Always verify at platform.openai.com/pricing
    RATES = {
        "gpt-3.5-turbo": 0.002 / 1000,
        "gpt-4":         0.03  / 1000
    }

    def __init__(self):
        self._requests = []

    def record(self, endpoint, question, model,
               tokens, latency_ms, success):
        cost = round(tokens * self.RATES.get(model, 0.002/1000), 6)
        self._requests.append({
            "timestamp":  datetime.now().isoformat(),
            "endpoint":   endpoint,
            "question":   question[:50],
            "model":      model,
            "tokens":     tokens,
            "cost_usd":   cost,
            "latency_ms": latency_ms,
            "success":    success
        })

    def stats(self):
        if not self._requests:
            return {"message": "No requests yet"}

        total      = len(self._requests)
        successful = sum(1 for r in self._requests if r["success"])
        latencies  = [r["latency_ms"] for r in self._requests]
        total_cost = sum(r["cost_usd"] for r in self._requests)
        total_tok  = sum(r["tokens"] for r in self._requests)

        return {
            "total_requests":    total,
            "successful":        successful,
            "error_rate":        round((total-successful)/total, 3),
            "p50_latency_ms":    round(statistics.median(latencies), 1),
            "p95_latency_ms":    round(
                sorted(latencies)[int(len(latencies)*0.95)], 1
            ),
            "total_tokens":      total_tok,
            "total_cost_usd":    round(total_cost, 4),
            "cost_note":         "Verify rates at platform.openai.com"
        }
