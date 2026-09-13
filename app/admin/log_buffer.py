"""In-memory ring buffer log handler backing GET /api/admin/logs.
A real deployment would ship logs to a proper aggregator; this is a
lightweight, dependency-free option that's genuinely useful for a small
single-instance deployment and satisfies the "Logs" admin permission."""
import logging
from collections import deque
from datetime import datetime

_BUFFER_SIZE = 500
_buffer: deque = deque(maxlen=_BUFFER_SIZE)


class RingBufferHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        _buffer.append({
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })


def get_recent_logs(limit: int = 200) -> list[dict]:
    return list(_buffer)[-limit:][::-1]  # most recent first
