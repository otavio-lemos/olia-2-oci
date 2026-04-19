"""Logging estruturado com trace_id."""

import json
import uuid
from datetime import datetime
from typing import Any, Optional
import logging


class JSONLogger:
    """Logger JSON estruturado."""

    def __init__(self, logger_name: str = "rag"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

    def log(
        self, level: str, action: str, trace_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Log com estrutura JSON."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "trace_id": trace_id or generate_trace_id(),
            "action": action,
            **kwargs,
        }

        # Log as JSON string
        self.logger.info(json.dumps(log_entry))


def generate_trace_id() -> str:
    """Gera trace ID único."""
    return f"trace-{uuid.uuid4().hex[:12]}"


def setup_logging(level: str = "INFO") -> None:
    """Configura logging global."""
    logging.basicConfig(level=getattr(logging, level), format="%(message)s")
