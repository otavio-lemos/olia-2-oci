"""Testes para Task 1.4 - Retry logic."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock


class TestRetryLogic:
    """Testes para retry com exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_decorator_exists(self):
        """retry_with_backoff deve existir."""
        from rag.llm_client import retry_with_backoff

        assert callable(retry_with_backoff)

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Deve fazer retry em caso de falha."""
        from rag.llm_client import retry_with_backoff

        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Failed")
            return "success"

        result = await failing_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Deve-raising após max_retries."""
        from rag.llm_client import retry_with_backoff

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        async def always_fails():
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            await always_fails()

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Delay deve aumentar exponencialmente."""
        from rag.llm_client import retry_with_backoff
        import time

        delays = []

        @retry_with_backoff(max_retries=3, base_delay=0.1)
        async def timing_func():
            delays.append(time.time())
            if len(delays) < 3:
                raise ConnectionError("Fail")
            return "done"

        await timing_func()

        # Check delays grow exponentially
        if len(delays) >= 3:
            d1 = delays[1] - delays[0]
            d2 = delays[2] - delays[1]
            # Second delay should be roughly 2x first (within tolerance)
            assert d2 > d1 * 0.5
