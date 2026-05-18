# logger.py — Request logging
# ══════════════════════════════════════════════
from datetime import datetime
class RequestLogger:
    """
    Logs every request with full details.
    In production: write to file or logging service.
    """
    def __init__(self):
        self._logs = []

    def log(self, level, endpoint, message, extra=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level":     level,
            "endpoint":  endpoint,
            "message":   message,
            "extra":     extra or {}
        }
        self._logs.append(entry)
        print(f"  [{level}] {endpoint} | {message}")

    def get_logs(self, level=None, limit=50):
        logs = self._logs
        if level:
            logs = [l for l in logs if l["level"] == level]
        return logs[-limit:]

