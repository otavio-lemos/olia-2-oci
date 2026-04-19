"""LLM Client - Interface unificada para MLX, llama.cpp e Ollama."""

import asyncio
import functools
from typing import Protocol, AsyncIterator, Any
from abc import abstractmethod


def retry_with_backoff(
    max_retries: int = 3, base_delay: float = 1.0, exponential: bool = True
):
    """Decorator retry com exponential backoff."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, OSError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2**attempt) if exponential else base_delay
                        await asyncio.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


class LLMClient(Protocol):
    """Interface para provedores de LLM local."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Gera resposta Síncrona."""
        ...

    @abstractmethod
    def stream(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Gera resposta com streaming de tokens."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Fecha conexao e libera recursos."""
        ...


def streaming_format(token: str, done: bool = False) -> str:
    """Formata token para SSE."""
    if done:
        return f"data: {token}\ndata: [DONE]\n\n"
    return f"data: {token}\n\n"


class MLXClient:
    """Client para MLX (Apple Silicon)."""

    def __init__(self, model: Any = None, adapter_path: str | None = None):
        self.model = model
        self.adapter_path = adapter_path
        self._loaded = False

    async def generate(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Gera resposta com MLX."""
        if not self._loaded:
            await self._load_model()
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        result = self.model.generate(
            full_prompt, temperature=temperature, max_tokens=max_tokens
        )
        return result

    async def stream(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Streaming com MLX."""
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        for token in self.model.stream_generate(full_prompt):
            yield token

    async def close(self) -> None:
        """Libera recursos."""
        if hasattr(self.model, "unload"):
            self.model.unload()
        self._loaded = False

    async def _load_model(self) -> None:
        """Carrega modelo."""
        if self.model is None:
            try:
                from mlx_lm import load as load_mlx

                model, tokenizer = load_mlx(
                    "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
                    adapter_path=self.adapter_path,
                )
                self.model = model
                self.tokenizer = tokenizer
            except ImportError:
                raise RuntimeError("MLX not installed. Install: pip install mlx-lm")
        self._loaded = True

    def _build_prompt(
        self, prompt: str, context: list[Any], system_prompt: str | None
    ) -> str:
        """Constrói prompt com contexto."""
        system = system_prompt or "Você é um especialista em OCI."
        context_str = ""
        if context:
            context_str = "\n\nContexto relevante:\n" + "\n---\n".join(
                [
                    d.page_content if hasattr(d, "page_content") else str(d)
                    for d in context
                ]
            )
        return f"SYSTEM: {system}\n\n{context_str}\n\nUSER: {prompt}\n\nASSISTANT:"


class LlamaCppClient:
    """Client para llama.cpp."""

    def __init__(self, model_path: str, model: Any = None):
        self.model_path = model_path
        self.model = model
        self._loaded = False

    async def generate(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Gera resposta com llama.cpp."""
        if not self._loaded:
            await self._load_model()
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        result = self.model.create_completion(
            prompt=full_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return result["choices"][0]["text"]

    def stream(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Streaming com llama.cpp."""
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        for token in self.model.create_completion(prompt=full_prompt, stream=True):
            yield token["choices"][0]["text"]

    async def close(self) -> None:
        """Libera recursos."""
        self.model = None
        self._loaded = False

    async def _load_model(self) -> None:
        """Carrega modelo."""
        try:
            from llama_cpp import Llama

            self.model = Llama(self.model_path, n_ctx=4096, n_threads=8)
        except ImportError:
            raise RuntimeError("llama-cpp-python not installed.")
        self._loaded = True

    def _build_prompt(
        self, prompt: str, context: list[Any], system_prompt: str | None
    ) -> str:
        """Constrói prompt com contexto."""
        system = system_prompt or "Você é um especialista em OCI."
        context_str = ""
        if context:
            context_str = "\n\nContexto relevante:\n" + "\n---\n".join(
                [
                    d.page_content if hasattr(d, "page_content") else str(d)
                    for d in context
                ]
            )
        return f"SYSTEM: {system}\n\n{context_str}\n\nUSER: {prompt}\n\nASSISTANT:"


class OllamaClient:
    """Client para Ollama."""

    def __init__(
        self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.session = None

    async def generate(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Gera resposta com Ollama."""
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            ) as resp:
                result = await resp.json()
        return result.get("response", "")

    def stream(
        self,
        prompt: str,
        context: list[Any],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Streaming com Ollama."""
        import aiohttp

        full_prompt = self._build_prompt(prompt, context, system_prompt)

        async def gen():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": full_prompt,
                        "stream": True,
                    },
                ) as resp:
                    async for chunk in resp.content:
                        if chunk:
                            yield chunk.decode()

        return gen()

    async def close(self) -> None:
        """Libera recursos."""
        pass

    def _build_prompt(
        self, prompt: str, context: list[Any], system_prompt: str | None
    ) -> str:
        """Constrói prompt com contexto."""
        system = system_prompt or "Você é um especialista em OCI."
        context_str = ""
        if context:
            context_str = "\n\nContexto relevante:\n" + "\n---\n".join(
                [
                    d.page_content if hasattr(d, "page_content") else str(d)
                    for d in context
                ]
            )
        return f"SYSTEM: {system}\n\n{context_str}\n\nUSER: {prompt}\n\nASSISTANT:"
