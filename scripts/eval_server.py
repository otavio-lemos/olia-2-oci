#!/usr/bin/env python3
"""Eval Server - HTTP server for parallel model evaluation.

Usage:
    # Terminal 1 - Base model:
    python scripts/eval_server.py --port 5010 --model-type base --cycle cycle-1

    # Terminal 2 - FT model:
    python scripts/eval_server.py --port 5011 --model-type ft --cycle cycle-1
"""

import argparse
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


def load_cycle_config(cycle_name: str) -> dict:
    """Load cycle configuration from outputs/{cycle}/config/{cycle}.env for reproducibility."""
    env_file = (
        Path(__file__).parent.parent
        / "outputs"
        / cycle_name
        / "config"
        / f"{cycle_name}.env"
    )
    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip('"')
    return config


class EvalHandler(BaseHTTPRequestHandler):
    model = None
    tokenizer = None
    sampler = None

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        request = json.loads(post_data.decode("utf-8"))

        prompt = request.get("prompt", "")
        system_prompt = request.get("system_prompt", "")
        max_tokens = request.get("max_tokens", 256)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        prompt_tokens = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )

        start = time.time()
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt_tokens,
            max_tokens=max_tokens,
            sampler=self.sampler,
            verbose=False,
        )
        elapsed = time.time() - start

        result = {"response": response, "elapsed": elapsed}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        else:
            self.send_error(404)


def main():
    parser = argparse.ArgumentParser(description="Eval Server")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--model-type", required=True, choices=["base", "ft"])
    parser.add_argument("--cycle", required=True)
    args = parser.parse_args()

    config = load_cycle_config(args.cycle)
    base_model_id = config.get("MODEL", "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit")
    output_dir = config.get("OUTPUT_DIR", f"outputs/{args.cycle}")

    project_root = Path(__file__).parent.parent
    adapter_path = project_root / output_dir / "adapters"
    merged_path = project_root / output_dir / "merged"

    print(f"Loading {args.model_type} model...")

    if args.model_type == "ft":
        if adapter_path.exists() and (adapter_path / "adapters.safetensors").exists():
            model_path = str(adapter_path)
            EvalHandler.model, EvalHandler.tokenizer = load(
                path_or_hf_repo=base_model_id,
                adapter_path=model_path,
            )
        elif merged_path.exists():
            EvalHandler.model, EvalHandler.tokenizer = load(
                path_or_hf_repo=str(merged_path),
            )
    else:
        EvalHandler.model, EvalHandler.tokenizer = load(
            path_or_hf_repo=base_model_id,
        )

    EvalHandler.sampler = make_sampler(temp=0.3, top_p=0.9, min_p=0.0, top_k=20)

    print(f"Starting HTTP server on port {args.port}...")
    server = HTTPServer(("localhost", args.port), EvalHandler)
    print(f"Server ready at http://localhost:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
