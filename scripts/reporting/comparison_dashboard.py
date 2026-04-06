#!/usr/bin/env python3
"""Comparison dashboard for base vs fine-tuned model results."""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict


class ComparisonDashboard:
    """Generate side-by-side comparison of base vs FT model performance."""

    def __init__(self):
        pass

    def load_results(self, base_file: Path, ft_file: Path) -> Dict[str, Any]:
        with open(base_file, "r") as f:
            base = json.load(f)
        with open(ft_file, "r") as f:
            ft = json.load(f)
        return {"base": base, "ft": ft}

    def compute_improvement(self, results: Dict) -> Dict[str, Any]:
        base_evals = results.get("base", {}).get("evaluations", [])
        ft_evals = results.get("ft", {}).get("evaluations", [])

        if not base_evals or not ft_evals:
            return {"error": "No evaluations found"}

        improvements = []
        for i in range(min(len(base_evals), len(ft_evals))):
            base_score = base_evals[i].get("overall_score", 0)
            ft_score = ft_evals[i].get("overall_score", 0)
            improvements.append(
                {
                    "index": i,
                    "base_score": base_score,
                    "ft_score": ft_score,
                    "delta": ft_score - base_score,
                    "category": ft_evals[i].get("category", "unknown"),
                }
            )

        avg_base = sum(i["base_score"] for i in improvements) / len(improvements)
        avg_ft = sum(i["ft_score"] for i in improvements) / len(improvements)

        category_improvement = defaultdict(lambda: {"deltas": []})
        for imp in improvements:
            category_improvement[imp["category"]]["deltas"].append(imp["delta"])

        for cat in category_improvement:
            deltas = category_improvement[cat]["deltas"]
            category_improvement[cat]["avg_delta"] = sum(deltas) / len(deltas)
            category_improvement[cat]["count"] = len(deltas)

        return {
            "total_comparisons": len(improvements),
            "avg_base_score": round(avg_base, 2),
            "avg_ft_score": round(avg_ft, 2),
            "avg_improvement": round(avg_ft - avg_base, 2),
            "improvement_percentage": round(
                (avg_ft - avg_base) / max(avg_base, 0.1) * 100, 1
            ),
            "category_improvement": dict(category_improvement),
        }

    def generate_html(self, results: Dict, improvement: Dict, output_path: Path):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        base_avg = improvement.get("avg_base_score", 0)
        ft_avg = improvement.get("avg_ft_score", 0)
        avg_delta = improvement.get("avg_improvement", 0)
        improvement_pct = improvement.get("improvement_percentage", 0)

        cat_improvements = improvement.get("category_improvement", {})
        sorted_cats = sorted(
            cat_improvements.items(), key=lambda x: x[1]["avg_delta"], reverse=True
        )

        delta_color = (
            "#27ae60" if avg_delta > 0 else "#e74c3c" if avg_delta < 0 else "#95a5a6"
        )

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base vs FT Comparison - OCI Specialist LLM</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                   color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .comparison-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 3em; font-weight: bold; }}
        .delta-positive {{ color: #27ae60; }}
        .delta-negative {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #11998e; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Base vs Fine-Tuned Model Comparison</h1>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="comparison-grid">
            <div class="metric-card">
                <h3>Base Model</h3>
                <div class="metric-value">{base_avg:.2f}</div>
            </div>
            <div class="metric-card">
                <h3>Fine-Tuned Model</h3>
                <div class="metric-value">{ft_avg:.2f}</div>
            </div>
        </div>
        
        <div class="metric-card" style="margin-top: 20px;">
            <h3>Overall Improvement: <span style="color: {delta_color};">{avg_delta:+.2f} ({improvement_pct:+.1f}%)</span></h3>
        </div>
        
        <div class="metric-card">
            <h2>Category-wise Improvement</h2>
            <table>
                <tr><th>Category</th><th>Avg Delta</th><th>Count</th></tr>
"""

        for cat, data in sorted_cats:
            delta = data["avg_delta"]
            delta_class = "delta-positive" if delta > 0 else "delta-negative"
            html += f"""<tr><td>{cat}</td><td class="{delta_class}">{delta:+.2f}</td><td>{data["count"]}</td></tr>\n"""

        html += """
            </table>
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html)

        print(f"Comparison dashboard generated: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate base vs FT comparison dashboard"
    )
    parser.add_argument(
        "--base", required=True, help="Base model evaluation results JSON"
    )
    parser.add_argument(
        "--ft", required=True, help="Fine-tuned model evaluation results JSON"
    )
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    dashboard = ComparisonDashboard()
    results = dashboard.load_results(Path(args.base), Path(args.ft))
    improvement = dashboard.compute_improvement(results)
    dashboard.generate_html(results, improvement, Path(args.output))


if __name__ == "__main__":
    main()
