#!/usr/bin/env python3
"""LRU cache for evaluation model responses."""

import json
import hashlib
import time
from pathlib import Path
from typing import Optional
from collections import OrderedDict
import threading


class EvalCache:
    """LRU cache for model responses to avoid redundant inference."""

    def __init__(self, cache_dir: str = "outputs/cache", max_entries: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self._memory_cache = OrderedDict()
        self._lock = threading.Lock()
        self._index_file = self.cache_dir / "cache_index.json"
        self._load_index()

    def _load_index(self):
        """Load cache index from disk."""
        if self._index_file.exists():
            try:
                with open(self._index_file, "r") as f:
                    index = json.load(f)
                    for k, v in index.items():
                        self._memory_cache[k] = v
            except:
                pass

    def _save_index(self):
        """Save cache index to disk."""
        with open(self._index_file, "w") as f:
            json.dump(dict(self._memory_cache), f)

    def _make_key(self, model_id: str, prompt: str) -> str:
        """Create cache key from model and prompt."""
        content = f"{model_id}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(self, model_id: str, prompt: str) -> Optional[str]:
        """Get cached response."""
        key = self._make_key(model_id, prompt)
        with self._lock:
            if key in self._memory_cache:
                self._memory_cache.move_to_end(key)
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    try:
                        with open(cache_file, "r") as f:
                            data = json.load(f)
                            return data.get("response")
                    except:
                        return None
        return None

    def put(self, model_id: str, prompt: str, response: str):
        """Store response in cache."""
        key = self._make_key(model_id, prompt)
        with self._lock:
            if key in self._memory_cache:
                self._memory_cache.move_to_end(key)
            else:
                if len(self._memory_cache) >= self.max_entries:
                    oldest_key = next(iter(self._memory_cache))
                    del self._memory_cache[oldest_key]
                    old_file = self.cache_dir / f"{oldest_key}.json"
                    if old_file.exists():
                        old_file.unlink()
                self._memory_cache[key] = {"added": time.time()}

            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, "w") as f:
                json.dump(
                    {"model_id": model_id, "prompt": prompt, "response": response}, f
                )
            self._save_index()

    def clear(self):
        """Clear all cached responses."""
        with self._lock:
            self._memory_cache.clear()
            for f in self.cache_dir.glob("*.json"):
                f.unlink()
            self._save_index()

    def stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            return {
                "entries": len(self._memory_cache),
                "max_entries": self.max_entries,
                "cache_dir": str(self.cache_dir),
            }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluation response cache")
    parser.add_argument("--clear", action="store_true", help="Clear cache")
    parser.add_argument("--stats", action="store_true", help="Show cache stats")
    args = parser.parse_args()

    cache = EvalCache()

    if args.clear:
        cache.clear()
        print("Cache cleared")
    elif args.stats:
        stats = cache.stats()
        print(f"Cache entries: {stats['entries']}/{stats['max_entries']}")
        print(f"Cache dir: {stats['cache_dir']}")
    else:
        print("Evaluation Cache")
        print(f"Directory: {cache.cache_dir}")
        stats = cache.stats()
        print(f"Entries: {stats['entries']}/{stats['max_entries']}")


if __name__ == "__main__":
    main()
