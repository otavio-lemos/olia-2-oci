"""Rate Limiter - Rate limiting por usuário."""

import time
from typing import Dict
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class UserLimit:
    """Dados de limite por usuário."""

    requests: list[float] = field(default_factory=list)
    blocked: bool = False


class RateLimiter:
    """Rate limiter com sliding window."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._user_limits: Dict[str, UserLimit] = defaultdict(UserLimit)

    def check(self, user_id: str) -> bool:
        """Verifica se request é permitido."""
        now = time.time()
        user_limit = self._user_limits[user_id]

        # Remove old requests outside window
        cutoff = now - self.window_seconds
        user_limit.requests = [t for t in user_limit.requests if t > cutoff]

        # Check limit
        if len(user_limit.requests) >= self.max_requests:
            user_limit.blocked = True
            return False

        # Allow and record
        user_limit.requests.append(now)
        user_limit.blocked = False
        return True

    def is_blocked(self, user_id: str) -> bool:
        """Retorna se usuário está bloqueado."""
        return self._user_limits[user_id].blocked

    def get_remaining(self, user_id: str) -> int:
        """Retorna requests restantes."""
        now = time.time()
        user_limit = self._user_limits[user_id]

        cutoff = now - self.window_seconds
        recent = [t for t in user_limit.requests if t > cutoff]

        return max(0, self.max_requests - len(recent))

    def reset(self, user_id: str) -> None:
        """Reseta limite para usuário."""
        if user_id in self._user_limits:
            del self._user_limits[user_id]


def create_rate_limiter(
    max_requests: int = 10, window_seconds: int = 60
) -> RateLimiter:
    """Factory para criar RateLimiter."""
    return RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
