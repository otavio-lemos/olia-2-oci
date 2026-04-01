#!/usr/bin/env python3
"""
Captura métricas de treinamento do mlx_lm lora.

Parsa output do treinamento e exporta:
- Log completo em arquivo
- Métricas estruturadas em CSV (step, train_loss, val_loss, timestamp)

Uso: python log_metrics.py <cycle_name> -- <comando de treinamento>
     python log_metrics.py cycle-1 -- python -m mlx_lm lora ...
"""

import csv
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_metrics(line, timestamp):
    """Extrai métricas de uma linha de output do mlx_lm."""
    metrics = {"timestamp": timestamp}

    # Iter N: Train loss X.XXX (step-based, from mlx_lm output)
    train_match = re.search(r"Iter (\d+).*[Ll]oss\s+([\d.]+)", line)
    if train_match:
        metrics["step"] = int(train_match.group(1))
        metrics["train_loss"] = float(train_match.group(2))

    # Val loss X.XXX
    val_match = re.search(r"Val loss\s+([\d.]+)", line)
    if val_match:
        metrics["val_loss"] = float(val_match.group(1))

    return metrics if len(metrics) > 1 else None


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    if "--" not in sys.argv:
        print(__doc__)
        sys.exit(1)

    cycle_name = sys.argv[1]
    train_cmd = sys.argv[sys.argv.index("--") + 1 :]

    logs_dir = Path("outputs/logs") / cycle_name
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "training.log"
    metrics_file = logs_dir / "metrics.csv"

    print(f"[log_metrics] Cycle: {cycle_name}")
    print(f"[log_metrics] Log: {log_file}")
    print(f"[log_metrics] Metrics: {metrics_file}")
    print(f"[log_metrics] Command: {' '.join(train_cmd)}")
    print()

    all_lines = []
    all_metrics = []

    process = subprocess.Popen(
        train_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    for line in process.stdout:
        line = line.rstrip("\n")
        print(line, flush=True)
        all_lines.append(line)

        timestamp = datetime.now(timezone.utc).isoformat()
        metrics = parse_metrics(line, timestamp)
        if metrics:
            all_metrics.append(metrics)

    return_code = process.wait()

    with open(log_file, "w") as f:
        f.write("\n".join(all_lines) + "\n")

    if all_metrics:
        fieldnames = ["step", "train_loss", "val_loss", "timestamp"]
        with open(metrics_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_metrics)
        print(
            f"\n[log_metrics] Exported {len(all_metrics)} metric rows to {metrics_file}"
        )
    else:
        print("\n[log_metrics] No metrics parsed from output")

    if return_code != 0:
        print(f"[log_metrics] Training exited with code {return_code}")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
