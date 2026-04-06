#!/usr/bin/env python3
"""Automated HTML report generator for evaluation results."""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict


class ReportGenerator:
    """Generate interactive HTML reports from evaluation results."""

    def __init__(self, template_dir: str = "scripts/reporting/templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def load_results(self, results_file: Path) -> Dict[str, Any]:
        """Load evaluation results from JSON."""
        with open(results_file, "r") as f:
            return json.load(f)

    def generate_category_breakdown(self, results: Dict) -> List[Dict]:
        """Generate category-wise performance breakdown."""
        category_scores = defaultdict(lambda: {"scores": [], "count": 0})

        for item in results.get("evaluations", []):
            category = item.get("category", "unknown")
            score = item.get("overall_score", 0)
            category_scores[category]["scores"].append(score)
            category_scores[category]["count"] += 1

        breakdown = []
        for cat, data in category_scores.items():
            avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            breakdown.append(
                {
                    "category": cat,
                    "avg_score": round(avg, 2),
                    "count": data["count"],
                    "min_score": min(data["scores"]) if data["scores"] else 0,
                    "max_score": max(data["scores"]) if data["scores"] else 0,
                }
            )

        return sorted(breakdown, key=lambda x: x["avg_score"])

    def generate_difficulty_analysis(self, results: Dict) -> List[Dict]:
        """Generate difficulty-wise performance analysis."""
        difficulty_scores = defaultdict(lambda: {"scores": [], "count": 0})

        for item in results.get("evaluations", []):
            difficulty = item.get("difficulty", "unknown")
            score = item.get("overall_score", 0)
            difficulty_scores[difficulty]["scores"].append(score)
            difficulty_scores[difficulty]["count"] += 1

        analysis = []
        for diff, data in difficulty_scores.items():
            avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            std = self._compute_std(data["scores"])
            analysis.append(
                {
                    "difficulty": diff,
                    "avg_score": round(avg, 2),
                    "count": data["count"],
                    "std_dev": std,
                }
            )

        return sorted(analysis, key=lambda x: x["avg_score"])

    def _compute_std(self, scores: List[float]) -> float:
        if not scores:
            return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return round(variance**0.5, 2)

    def generate_html(self, results: Dict, output_path: Path):
        """Generate complete HTML report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        category_breakdown = self.generate_category_breakdown(results)
        difficulty_analysis = self.generate_difficulty_analysis(results)

        evaluations = results.get("evaluations", [])
        overall_avg = sum(item.get("overall_score", 0) for item in evaluations) / max(
            len(evaluations), 1
        )

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCI Specialist LLM - Evaluation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .score-high {{ color: #27ae60; font-weight: bold; }}
        .score-medium {{ color: #f39c12; font-weight: bold; }}
        .score-low {{ color: #e74c3c; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OCI Specialist LLM - Evaluation Report</h1>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="metric-card">
            <h2>Overall Performance</h2>
            <div class="metric-value">{overall_avg:.2f}/5.0</div>
            <p>Total evaluations: {len(evaluations)}</p>
        </div>
        
        <div class="metric-card">
            <h2>Category Performance</h2>
            <table>
                <tr><th>Category</th><th>Avg Score</th><th>Count</th><th>Min</th><th>Max</th></tr>
"""

        for cat in category_breakdown:
            score_class = (
                "score-high"
                if cat["avg_score"] >= 4.0
                else "score-medium"
                if cat["avg_score"] >= 3.0
                else "score-low"
            )
            html += f"""<tr><td>{cat["category"]}</td><td class="{score_class}">{cat["avg_score"]}</td><td>{cat["count"]}</td><td>{cat["min_score"]}</td><td>{cat["max_score"]}</td></tr>\n"""

        html += """
            </table>
        </div>
        
        <div class="metric-card">
            <h2>Difficulty Analysis</h2>
            <table>
                <tr><th>Difficulty</th><th>Avg Score</th><th>Count</th><th>Std Dev</th></tr>
"""

        for diff in difficulty_analysis:
            score_class = (
                "score-high"
                if diff["avg_score"] >= 4.0
                else "score-medium"
                if diff["avg_score"] >= 3.0
                else "score-low"
            )
            html += f"""<tr><td>{diff["difficulty"]}</td><td class="{score_class}">{diff["avg_score"]}</td><td>{diff["count"]}</td><td>{diff["std_dev"]}</td></tr>\n"""

        html += """
            </table>
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html)

        print(f"Report generated: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate HTML evaluation reports")
    parser.add_argument(
        "--results", required=True, help="Path to evaluation results JSON"
    )
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    generator = ReportGenerator()
    results = generator.load_results(Path(args.results))
    generator.generate_html(results, Path(args.output))


if __name__ == "__main__":
    main()
