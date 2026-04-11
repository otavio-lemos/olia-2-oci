#!/usr/bin/env python3
"""Unified Evaluation Script for OCI Specialist LLM (Optimized for High Performance).

Consolida: base vs FT comparison, scoring, similarity semântica, relatórios com gráficos.
Modos: --cycle cycle-1 --mode test (10 samples), --mode full (1930 samples)

Usage:
    python scripts/unified_evaluation.py --cycle cycle-1 --mode test --batch-size 16
    python scripts/unified_evaluation.py --cycle cycle-1 --mode full --batch-size 16
"""

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import random
import gc

import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


def load_cycle_config(cycle_name: str) -> dict:
    """Load cycle configuration from config/cycle-N.env file."""
    env_file = Path(__file__).parent.parent / "config" / f"{cycle_name}.env"
    if not env_file.exists():
        raise FileNotFoundError(f"Config not found: {env_file}")

    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip('"')
    return config


# Dependências opcionais
try:
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False


class ScoringEngine:
    """Engine for evaluating OCI Specialist LLM responses (Optimized)."""

    REAL_CLI_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
        r"oci\s+(compute|network|db|bv|os|ce|fn|kms|vault|iam|logging|monitoring|resource-manager|devops|container-instance|nosql|mysql|cloud-guard|waas|apm|stack-monitoring|file-storage|load-balancer|api-gateway)",
        r"oci_core_instance",
        r"oci_objectstorage_bucket",
        r"oci_database_autonomous_database",
        r"oci_containerengine_cluster",
        r"oci\.core\.ComputeClient",
        r"oci\.object_storage\.ObjectStorageClient",
        r"oci\.database\.DatabaseClient",
    ]]
    
    FAKE_CLI_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
        r"oci\s+instances\s+",
        r"oci\s+storage\s+",
        r"oci\s+connectivity\s+",
        r"oci\s+block\s+",
        r"oci\s+autonomous-json\s+",
        r"oci\s+azure-storage\s+",
        r"oci\s+onprem-storage\s+",
        r"oci\s+observability\s+",
        r"oci\s+authentication\s+",
        r"oci\.Compute\.InstancesClient",
        r"oci\.Storage\.BlockClient",
        r"oci\.ConnectivityClient",
        r"oci_compute_instances",
        r"oci_storage_block",
        r"oci_connectivity",
    ]]

    CROSS_CLOUD_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
        r"provider\s+[\"']?aws[\"']?",
        r"resource\s+[\"']?aws_",
        r"resource\s+[\"']?azurerm_",
        r"aws_instance",
        r"aws_lb",
        r"aws_vpc",
        r"aws_security_group",
        r"aws_s3",
        r"aws_iam",
        r"azurerm_network_security_group",
        r"azurerm_virtual_network",
        r"azurerm_subnet",
        r"azurerm_public_ip",
        r"\bEC2\b",
        r"\bCloudWatch\b",
        r"AWS Management Console",
        r"Azure Portal",
    ]]

    DEPTH_INDICATORS = [
        (re.compile(r"\d+\.\s+"), 0.3),
        (re.compile(r"```"), 0.5),
        (re.compile(r"- "), 0.2),
        (re.compile(r"\* "), 0.2),
        (re.compile(r"best practice", re.IGNORECASE), 0.3),
        (re.compile(r"recomenda[çc][aã]o", re.IGNORECASE), 0.2),
        (re.compile(r"trade.?off", re.IGNORECASE), 0.3),
        (re.compile(r"vantagem", re.IGNORECASE), 0.2),
        (re.compile(r"desvantagem", re.IGNORECASE), 0.2),
        (re.compile(r"risco", re.IGNORECASE), 0.3),
        (re.compile(r"mitiga[çc][aã]o", re.IGNORECASE), 0.3),
        (re.compile(r"pr[ée]-requisito", re.IGNORECASE), 0.2),
        (re.compile(r"valida[çc][aã]o", re.IGNORECASE), 0.2),
    ]

    STRUCTURE_NUMBERED = re.compile(r"\d+\.\s+")
    STRUCTURE_BULLET = re.compile(r"^[-*]\s+", re.MULTILINE)
    STRUCTURE_SECTIONS = re.compile(r"#+\s+")

    HALLUCINATION_PATTERNS = [
        (re.compile(r"oci\s+instances\s+", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+storage\s+(?!gateway)", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+connectivity\s+", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+block\s+(?!volume)", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+autonomous-json", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+azure-storage", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+onprem-storage", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+observability\s+", re.IGNORECASE), 1.5),
        (re.compile(r"oci\s+authentication\s+", re.IGNORECASE), 1.5),
        (re.compile(r"oci\.Compute\.InstancesClient", re.IGNORECASE), 1.5),
        (re.compile(r"oci\.Storage\.BlockClient", re.IGNORECASE), 1.5),
        (re.compile(r"oci\.ConnectivityClient", re.IGNORECASE), 1.5),
        (re.compile(r"oci_compute_instances", re.IGNORECASE), 1.5),
        (re.compile(r"oci_storage_block", re.IGNORECASE), 1.5),
        (re.compile(r"oci_connectivity", re.IGNORECASE), 1.5),
        (re.compile(r"semidesenvolvimento", re.IGNORECASE), 1.0),
        (re.compile(r"Carneval", re.IGNORECASE), 1.0),
        (re.compile(r"Insurance", re.IGNORECASE), 0.5),
        (re.compile(r"deletar", re.IGNORECASE), 0.3),
    ]

    HALLUCINATION_CROSS_CLOUD = [
        (re.compile(r"provider\s+[\"']?aws[\"']?", re.IGNORECASE), 2.0),
        (re.compile(r"resource\s+[\"']?aws_", re.IGNORECASE), 2.0),
        (re.compile(r"resource\s+[\"']?azurerm_", re.IGNORECASE), 2.0),
        (re.compile(r"aws_instance", re.IGNORECASE), 2.0),
        (re.compile(r"aws_lb", re.IGNORECASE), 2.0),
        (re.compile(r"aws_vpc", re.IGNORECASE), 2.0),
        (re.compile(r"aws_security_group", re.IGNORECASE), 2.0),
        (re.compile(r"aws_s3", re.IGNORECASE), 2.0),
        (re.compile(r"aws_iam", re.IGNORECASE), 2.0),
        (re.compile(r"azurerm_network_security_group", re.IGNORECASE), 2.0),
        (re.compile(r"azurerm_virtual_network", re.IGNORECASE), 2.0),
        (re.compile(r"azurerm_subnet", re.IGNORECASE), 2.0),
        (re.compile(r"azurerm_public_ip", re.IGNORECASE), 2.0),
        (re.compile(r"EC2", re.IGNORECASE), 1.5),
        (re.compile(r"CloudWatch", re.IGNORECASE), 1.0),
        (re.compile(r"AWS Management Console", re.IGNORECASE), 1.5),
        (re.compile(r"AWS Console", re.IGNORECASE), 1.0),
        (re.compile(r"Amazon Web Services", re.IGNORECASE), 1.0),
        (re.compile(r"Azure Portal", re.IGNORECASE), 1.0),
        (re.compile(r"Azure Resource Manager", re.IGNORECASE), 1.0),
    ]

    FAKE_URLS = [
        re.compile(r"/Content/\w+/Con/\w+\.htm"),
        re.compile(r"/Content/\w+/-\w+\.htm"),
    ]

    CLARITY_CONJUNCTIONS = re.compile(r"\b(portanto|assim|consequentemente|dessa forma|em resumo)\b", re.IGNORECASE)
    CLARITY_EXAMPLES = re.compile(r"\b(exemplo|por exemplo|como segue|veja que)\b", re.IGNORECASE)

    @classmethod
    def score_technical_correctness(cls, response: str, category: str) -> float:
        score = 3.0
        if not response or response.startswith("Error:"):
            return 1.0
        if len(response) < 100:
            score -= 1.0
            
        has_real = any(p.search(response) for p in cls.REAL_CLI_PATTERNS)
        has_fake = any(p.search(response) for p in cls.FAKE_CLI_PATTERNS)
        has_cross_cloud = any(p.search(response) for p in cls.CROSS_CLOUD_PATTERNS)
        
        if has_fake:
            score -= 2.0
        if has_cross_cloud:
            score -= 2.5
        if has_real:
            score += 1.0
            
        terraform_cats = [
            "terraform/provider",
            "terraform/compute",
            "terraform/storage",
            "terraform/networking",
            "terraform/database",
            "terraform/container",
            "terraform/serverless",
            "terraform/security",
            "terraform/observability",
            "terraform/devops",
            "terraform/state",
        ]
        
        lower_resp = response.lower()
        if category in terraform_cats:
            if "terraform" in lower_resp and (
                "resource" in lower_resp or "provider" in lower_resp
            ):
                score += 0.5
            if "oci_" in response:
                score += 0.5
                
        if "Allow group" in response and "to" in response and "in compartment" in response:
            score += 0.5
        if "Doc:" in response or "docs.oracle.com" in response:
            score += 0.3
            
        return max(1.0, min(5.0, score))

    @classmethod
    def score_depth(cls, response: str) -> float:
        score = 3.0
        if not response or response.startswith("Error:"):
            return 1.0
            
        for pattern, points in cls.DEPTH_INDICATORS:
            if pattern.search(response):
                score += points
                
        word_count = len(response.split())
        if word_count > 200:
            score += 0.5
        if word_count > 500:
            score += 0.5
        if word_count < 50:
            score -= 1.0
            
        return max(1.0, min(5.0, score))

    @classmethod
    def score_structure(cls, response: str) -> float:
        score = 3.0
        if not response or response.startswith("Error:"):
            return 1.0
            
        has_numbered_list = bool(cls.STRUCTURE_NUMBERED.search(response))
        has_bullet_list = bool(cls.STRUCTURE_BULLET.search(response))
        has_code_block = "```" in response
        has_sections = bool(cls.STRUCTURE_SECTIONS.search(response))
        has_table = "|" in response and "---" in response
        
        structural_elements = sum([
            has_numbered_list,
            has_bullet_list,
            has_code_block,
            has_sections,
            has_table,
        ])
        
        if structural_elements >= 3:
            score += 1.5
        elif structural_elements >= 2:
            score += 1.0
        elif structural_elements >= 1:
            score += 0.5
            
        if len(response.split("\n")) > 10:
            score += 0.3
            
        return max(1.0, min(5.0, score))

    @classmethod
    def score_hallucination(cls, response: str) -> float:
        score = 5.0
        if not response or response.startswith("Error:"):
            return 1.0
            
        for pattern, penalty in cls.HALLUCINATION_PATTERNS:
            if pattern.search(response):
                score -= penalty
        for pattern, penalty in cls.HALLUCINATION_CROSS_CLOUD:
            if pattern.search(response):
                score -= penalty
        for pattern in cls.FAKE_URLS:
            if pattern.search(response):
                score -= 1.0
                
        return max(1.0, min(5.0, score))

    @classmethod
    def score_clarity(cls, response: str) -> float:
        score = 3.0
        if not response or response.startswith("Error:"):
            return 1.0
            
        length = len(response)
        if length < 50:
            score -= 1.5
        elif length < 100:
            score -= 0.5
        if length > 2000:
            score -= 0.3
            
        sentences = re.split(r"[.!?]+", response)
        avg_sentence_length = len(response.split()) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 25:
            score += 0.5
            
        if cls.CLARITY_CONJUNCTIONS.search(response):
            score += 0.3
        if cls.CLARITY_EXAMPLES.search(response):
            score += 0.3
            
        return max(1.0, min(5.0, score))

    @classmethod
    def evaluate_response_fast(
        cls, response: str, reference: str, category: str, similarity: float
    ) -> Dict[str, Any]:
        """Fast scoring that directly accepts precomputed semantic similarity."""
        # Scale from 0.0-1.0 to 1.0-5.0
        def scale_to_5(score_0_to_1):
            return 1.0 + (score_0_to_1 * 4.0)

        factual = min(1.0, similarity * 1.2)
        coverage = similarity if similarity > 0.5 else similarity * 0.8

        scores = {
            "technical_correctness": scale_to_5(factual),
            "depth": scale_to_5(coverage),
            "structure": cls.score_structure(response),
            "hallucination": scale_to_5(similarity),
            "clarity": cls.score_clarity(response),
        }
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores


class SemanticScorer:
    """Lightweight semantic similarity for hallucination detection with Batching."""

    def __init__(
        self, model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    ):
        self.model_name = model_name
        self.model = None
        self.embedding_cache = {}

    def load_model(self):
        """Lazy load embedding model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
                print(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                print(
                    "Warning: sentence-transformers not installed. Using fallback TF-IDF similarity."
                )
                self.model = None

    def get_embedding(self, text: str):
        """Get embedding for text with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        if self.model is None:
            return self._tfidf_fallback(text)

        embedding = self.model.encode(text, convert_to_numpy=True)
        self.embedding_cache[text] = embedding
        return embedding

    def _tfidf_fallback(self, text: str):
        """Simple word hashing fallback when sentence-transformers not available."""
        import numpy as np

        words = text.lower().split()
        vector = np.zeros(128)
        for i, word in enumerate(words[:128]):
            vector[i % 128] += hash(word) % 100 / 100.0
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        import numpy as np

        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(emb1, emb2) / (norm1 * norm2))
        
    def compute_similarity_batch(self, texts1: List[str], texts2: List[str]) -> List[float]:
        """Compute cosine similarity between two lists of texts efficiently."""
        if not texts1 or not texts2:
            return []
            
        if self.model is None:
            # Fallback to sequential if missing library
            return [self.compute_similarity(t1, t2) for t1, t2 in zip(texts1, texts2)]

        import numpy as np

        # Encode references missing in cache
        unique_texts1 = list(set(texts1))
        texts1_to_encode = [t for t in unique_texts1 if t not in self.embedding_cache]
        if texts1_to_encode:
            embs = self.model.encode(texts1_to_encode, batch_size=64, convert_to_numpy=True, show_progress_bar=False)
            for t, e in zip(texts1_to_encode, embs):
                self.embedding_cache[t] = e
        
        # Encode responses missing in cache
        unique_texts2 = list(set(texts2))
        texts2_to_encode = [t for t in unique_texts2 if t not in self.embedding_cache]
        if texts2_to_encode:
            embs = self.model.encode(texts2_to_encode, batch_size=64, convert_to_numpy=True, show_progress_bar=False)
            for t, e in zip(texts2_to_encode, embs):
                self.embedding_cache[t] = e

        emb1 = np.array([self.embedding_cache[t] for t in texts1])
        emb2 = np.array([self.embedding_cache[t] for t in texts2])

        norm1 = np.linalg.norm(emb1, axis=1)
        norm2 = np.linalg.norm(emb2, axis=1)
        
        # Prevent division by zero
        norm1[norm1 == 0] = 1e-10
        norm2[norm2 == 0] = 1e-10

        sims = np.sum(emb1 * emb2, axis=1) / (norm1 * norm2)
        return sims.tolist()


class ReportGenerator:
    """Generates markdown reports and charts for evaluation results."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_comparison_report(
        self,
        base_results: List[Dict],
        ft_results: List[Dict],
        total_eval: int,
    ) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"comparison_report_{timestamp}.md"

        base_avg = self._compute_average(base_results) if base_results else {}
        ft_avg = self._compute_average(ft_results) if ft_results else {}

        lines = [
            "# Evaluation Comparison Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Evaluated:** {total_eval}",
            "",
            "## Summary",
            "",
            "| Metric | Base Model | Fine-Tuned | Delta |",
            "|--------|-------------|------------|-------|",
        ]

        metrics = [
            "technical_correctness",
            "depth",
            "structure",
            "hallucination",
            "clarity",
            "overall",
        ]
        for metric in metrics:
            base_val = base_avg.get(metric, 0)
            ft_val = ft_avg.get(metric, 0)
            delta = ft_val - base_val
            delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"
            lines.append(f"| {metric} | {base_val:.2f} | {ft_val:.2f} | {delta_str} |")

        if base_results and ft_results:
            lines.extend(
                [
                    "",
                    "## Detailed Results",
                    "",
                    "| # | Category | Base | FT | Delta |",
                    "|---|---------|------|----|-------|",
                ]
            )
            categories = set()
            for r in base_results + ft_results:
                if "category" in r:
                    categories.add(r["category"])
            for i, cat in enumerate(sorted(categories), 1):
                base_cat = next(
                    (
                        r.get("scores", {}).get("overall", 0)
                        for r in base_results
                        if r.get("category") == cat
                    ),
                    0,
                )
                ft_cat = next(
                    (
                        r.get("scores", {}).get("overall", 0)
                        for r in ft_results
                        if r.get("category") == cat
                    ),
                    0,
                )
                delta = ft_cat - base_cat
                delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"
                lines.append(
                    f"| {i} | {cat} | {base_cat:.2f} | {ft_cat:.2f} | {delta_str} |"
                )

        with open(report_path, "w") as f:
            f.write("\n".join(lines))

        print(f"Report generated: {report_path}")
        return report_path

    def generate_charts(
        self,
        base_results: List[Dict],
        ft_results: List[Dict],
    ) -> List[Path]:
        if not HAS_PLOTTING:
            return []

        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns

        chart_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        base_avg = self._compute_average(base_results) if base_results else {}
        ft_avg = self._compute_average(ft_results) if ft_results else {}

        metrics = [
            "technical_correctness",
            "depth",
            "structure",
            "hallucination",
            "clarity",
            "overall",
        ]
        base_vals = [base_avg.get(m, 0) for m in metrics]
        ft_vals = [ft_avg.get(m, 0) for m in metrics]

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(metrics))
        width = 0.35
        ax.bar(x - width / 2, base_vals, width, label="Base Model", alpha=0.8)
        ax.bar(x + width / 2, ft_vals, width, label="Fine-Tuned", alpha=0.8)
        ax.set_ylabel("Score")
        ax.set_title("Model Comparison by Metric")
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha="right")
        ax.legend()
        ax.set_ylim(1, 5.5)
        plt.tight_layout()

        chart_path = self.output_dir / f"comparison_chart_{timestamp}.png"
        plt.savefig(chart_path, dpi=150)
        plt.close()
        chart_paths.append(chart_path)

        categories = set()
        for r in base_results + ft_results:
            if "category" in r:
                categories.add(r["category"])

        if categories:
            cat_metrics = []
            for cat in sorted(categories):
                base_cat = next(
                    (
                        r.get("scores", {}).get("overall", 0)
                        for r in base_results
                        if r.get("category") == cat
                    ),
                    0,
                )
                ft_cat = next(
                    (
                        r.get("scores", {}).get("overall", 0)
                        for r in ft_results
                        if r.get("category") == cat
                    ),
                    0,
                )
                cat_metrics.append((cat, base_cat, ft_cat))

            fig, ax = plt.subplots(figsize=(12, 6))
            cats = [c[0] for c in cat_metrics]
            base_cats = [c[1] for c in cat_metrics]
            ft_cats = [c[2] for c in cat_metrics]
            x = np.arange(len(cats))
            ax.bar(x - width / 2, base_cats, width, label="Base Model", alpha=0.8)
            ax.bar(x + width / 2, ft_cats, width, label="Fine-Tuned", alpha=0.8)
            ax.set_ylabel("Score")
            ax.set_title("Model Comparison by Category")
            ax.set_xticks(x)
            ax.set_xticklabels(cats, rotation=45, ha="right")
            ax.legend()
            ax.set_ylim(1, 5.5)
            plt.tight_layout()

            cat_chart_path = self.output_dir / f"category_chart_{timestamp}.png"
            plt.savefig(cat_chart_path, dpi=150)
            plt.close()
            chart_paths.append(cat_chart_path)

        for chart_path in chart_paths:
            print(f"Chart generated: {chart_path}")

        return chart_paths

    def _compute_average(self, results: List[Dict]) -> Dict[str, float]:
        if not results:
            return {}
        metric_keys = [
            "technical_correctness",
            "depth",
            "structure",
            "hallucination",
            "clarity",
            "overall",
        ]
        totals = {k: 0.0 for k in metric_keys}
        count = 0
        for r in results:
            scores = r.get("scores", {})
            for key in metric_keys:
                if key in scores:
                    totals[key] += scores[key]
            count += 1
        if count == 0:
            return {}
        return {k: v / count for k, v in totals.items()}


class UnifiedEvaluator:
    def __init__(
        self,
        base_model_id: str,
        adapter_path: str = "",
        merged_model_path: str = "",
        batch_size: int = 16,
    ):
        self.base_model_id = base_model_id
        self.adapter_path = adapter_path
        self.merged_model_path = merged_model_path
        self.batch_size = batch_size
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load_model(self):
        """Carrega modelo base ou FT."""
        if self._loaded:
            return

        if self.merged_model_path:
            print(f"Loading merged model: {self.merged_model_path}")
            self.model, self.tokenizer = load(path_or_hf_repo=self.merged_model_path)
        else:
            print(f"Loading model: {self.base_model_id}")
            if self.adapter_path:
                print(f"  With adapter: {self.adapter_path}")
            self.model, self.tokenizer = load(
                path_or_hf_repo=self.base_model_id,
                adapter_path=self.adapter_path if self.adapter_path else None,
            )

        self.sampler = make_sampler(temp=0.3, top_p=0.9, min_p=0.0, top_k=20)
        self._loaded = True
        print("Model loaded successfully")

    def generate_response(
        self, prompt: str, system_prompt: str = "", max_tokens: int = 512
    ) -> str:
        if not self._loaded:
            self.load_model()

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

        return response, elapsed

    def generate_batch(
        self, prompts: List[tuple], max_tokens: int = 512
    ) -> List[tuple]:
        """Generate responses."""
        if not self._loaded:
            self.load_model()

        results = []
        total = len(prompts)
        batch_size = self.batch_size

        if batch_size <= 1:
            print(f"  Processing {total} prompts sequentially (Optimized for early-stopping)...")
            start_all = time.time()
            for i, (user_prompt, system_prompt) in enumerate(prompts):
                resp, t = self.generate_response(user_prompt, system_prompt, max_tokens)
                results.append((resp, t))
                
                # Exibir progresso a cada 10 amostras
                if (i + 1) % 10 == 0:
                    avg_t = sum(r[1] for r in results) / len(results)
                    print(f"    [{i+1:3d}/{total}] Avg time per prompt: {avg_t:.2f}s")
            
            total_time = time.time() - start_all
            print(f"\n  Total: {total} prompts in {total_time:.1f}s ({total / total_time:.1f} prompts/sec)")
            return results

        from mlx_lm import batch_generate

        print(f"  Processing {total} prompts in batches of {batch_size}...")

        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch_prompts = prompts[batch_start:batch_end]

            # Prepare prompts as tokenized list
            prompt_list = []
            for user_prompt, system_prompt in batch_prompts:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_prompt})

                # Mlx-lm batch_generate usually expects string prompts or token IDs.
                # apply_chat_template mostly returns a string if tokenize is False or implicit depending on tokenizer config.
                # However, it works identically to original format this way.
                prompt_tokens = self.tokenizer.apply_chat_template(
                    messages, add_generation_prompt=True
                )
                prompt_list.append(prompt_tokens)

            try:
                batch_start_time = time.time()
                batch_response = batch_generate(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    prompts=prompt_list,
                    max_tokens=max_tokens,
                    sampler=self.sampler,
                    prefill_batch_size=batch_size,
                    completion_batch_size=batch_size,
                    verbose=False,
                )
                batch_elapsed = time.time() - batch_start_time

                # batch_response can be a list of outputs or have a texts attribute
                gen_responses = batch_response.texts if hasattr(batch_response, "texts") else batch_response
                for text in gen_responses:
                    results.append((str(text), batch_elapsed / len(batch_prompts)))

            except Exception as e:
                print(f"    Batch {batch_start}-{batch_end} failed: {e}")
                # Fallback to sequential for this batch
                for user_prompt, system_prompt in batch_prompts:
                    try:
                        resp, t = self.generate_response(
                            user_prompt, system_prompt, max_tokens
                        )
                        results.append((resp, t))
                    except Exception as ex:
                        results.append((f"Error: {str(ex)}", 0.0))
                batch_elapsed = 0.0

            batch_num = (batch_start // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            prompts_count = len(batch_prompts)
            prompts_per_sec = prompts_count / batch_elapsed if batch_elapsed > 0 else 0
            print(
                f"    Batch {batch_num:2d}/{total_batches}: {prompts_count} prompts | {batch_elapsed:.1f}s | {prompts_per_sec:.2f} prompts/sec | {batch_start + len(batch_prompts)}/{total}"
            )

            # Clear cache between batches to prevent memory leaking
            mx.clear_cache()
            gc.collect()

        total_time = sum(t for _, t in results)
        prompts_per_sec = total / total_time if total_time > 0 else 0
        print(
            f"\n  Total: {total} prompts in {total_time:.1f}s ({prompts_per_sec:.1f} prompts/sec)"
        )

        return results[:total]


def load_eval_data(eval_file: str) -> List[Dict]:
    """Load evaluation data from JSONL file."""
    data = []
    with open(eval_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def sample_per_category(data: List[Dict], samples: int = 10) -> List[Dict]:
    """Sample n examples from different categories (max 1 per category)."""
    random.seed(42)
    by_category = {}
    for item in data:
        cat = item.get("metadata", {}).get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)

    categories = list(by_category.keys())
    random.shuffle(categories)

    selected_cats = categories[:samples]
    sampled = []
    for cat in selected_cats:
        sampled.append(random.choice(by_category[cat]))
    return sampled


def sample_stratified(data: List[Dict], samples: int = 200) -> List[Dict]:
    """Sample n examples stratified by category (proportional representation)."""
    random.seed(42)
    by_category = {}
    for item in data:
        cat = item.get("metadata", {}).get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)

    total = len(data)
    sampled = []
    for cat, items in by_category.items():
        proportion = len(items) / total
        n_samples = max(1, round(samples * proportion))
        n_samples = min(n_samples, len(items))
        selected = random.sample(items, n_samples)
        sampled.extend(selected)

    random.shuffle(sampled)
    return sampled[:samples]


def evaluate_model(
    evaluator: UnifiedEvaluator,
    eval_data: List[Dict],
    semantic_scorer: Optional[SemanticScorer] = None,
    mode: str = "base",
    resume_results: List[Dict] = None,
    checkpoint_file: Path = None,
) -> List[Dict]:
    """Run evaluation loop for a model using batch processing."""
    total = len(eval_data)

    # Handle resume from checkpoint
    results = resume_results if resume_results else []
    start_idx = len(results)

    if start_idx > 0:
        print(f"[{mode}] Resuming from index {start_idx}/{total}")
        # Slice eval_data to start from where we left off
        eval_data = eval_data[start_idx:]

    # Prepare all prompts
    prompts = []
    references = []
    categories = []

    for item in eval_data:
        messages = item.get("messages", [])
        system_prompt = ""
        user_prompt = ""

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                system_prompt = content
            elif role == "user":
                user_prompt = content

        reference = ""
        for msg in messages:
            if msg.get("role") == "assistant":
                reference = msg.get("content", "")
                break

        category = item.get("metadata", {}).get("category", "unknown")

        prompts.append((user_prompt, system_prompt))
        references.append(reference)
        categories.append(category)

    print(f"[{mode}] Processing {total} samples in batch...")

    # Run batch generation
    try:
        # Pass max_tokens=512 exactly as requested.
        responses, elapsed = evaluator.generate_batch(prompts, max_tokens=512)
    except Exception as e:
        print(f"Batch generation failed: {e}, falling back to sequential")
        responses = []
        elapsed = 0.0
        for i, (user_prompt, system_prompt) in enumerate(prompts):
            print(f"[{mode}] {i + 1}/{total}: {categories[i]}")
            try:
                resp, t = evaluator.generate_response(
                    user_prompt, system_prompt=system_prompt, max_tokens=512
                )
                responses.append((resp, t))
                elapsed += t
            except Exception as ex:
                responses.append((f"Error: {str(ex)}", 0.0))

    # Score all responses efficiently in batch
    print(f"[{mode}] Evaluating generated responses...")
    sem_sims = [0.5] * len(responses)
    if semantic_scorer and any(references):
        try:
            # Batch compute similarities using vectorized sentence-transformers
            sem_sims = semantic_scorer.compute_similarity_batch(references, [r[0] for r in responses])
        except Exception as e:
            print(f"Batch semantic scoring failed: {e}")

    results_eval = []
    for i, (response, response_time) in enumerate(responses):
        reference = references[i]
        category = categories[i]
        sim = sem_sims[i]

        scores = ScoringEngine.evaluate_response_fast(response, reference, category, sim)

        result = {
            "category": category,
            "prompt": prompts[i][0],
            "response": response,
            "reference": reference,
            "scores": scores,
            "semantic_similarity": float(sim),
            "elapsed_seconds": response_time,
            "model": mode,
        }
        results_eval.append(result)

        # Save checkpoint periodically
        if checkpoint_file and (i + 1) % 50 == 0:
            save_results(results + results_eval, checkpoint_file)
            print(f"  [{mode}] Checkpoint saved at {start_idx + i + 1}/{total + start_idx}")

    return results + results_eval


def save_results(results: List[Dict], output_path: Path):
    """Save evaluation results to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Unified OCI Specialist Evaluation (Optimized)")
    parser.add_argument("--cycle", required=True, help="Cycle name (e.g., cycle-1)")
    parser.add_argument(
        "--mode",
        choices=["small", "medium", "full", "test"],
        default="medium",
        help="Eval mode: small/test (10), medium (200), full (1930)",
    )
    parser.add_argument(
        "--test-samples", type=int, default=10, help="Samples count (small/test mode)"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=200,
        help="Samples count (medium mode, default: 200)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for parallel generation. Use 1 (default) for variable length outputs (much faster), or 8/16 for fixed lengths.",
    )
    parser.add_argument(
        "--fresh", action="store_true", help="Clear output directory before running"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Also evaluate base model for comparison"
    )
    parser.add_argument("--eval-file", default="data/eval.jsonl", help="Eval JSONL")
    parser.add_argument("--output-dir", default="outputs/benchmarks", help="Output dir")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--merged", default="", help="Merged model path (optional override)"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    config = load_cycle_config(args.cycle)

    base_model_id = config.get("MODEL", "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    output_dir_config = config.get("OUTPUT_DIR", f"outputs/{args.cycle}")

    # Auto-detect merged model or use adapter
    merged_path = project_root / output_dir_config / "merged"
    adapter_path = str(project_root / output_dir_config / "adapters")

    # Use merged model if available, otherwise use adapter
    if merged_path.exists():
        ft_model_path = str(merged_path)
        ft_mode = "merged"
    else:
        ft_model_path = adapter_path
        ft_mode = "adapter"

    eval_file = args.eval_file
    output_dir = Path(args.output_dir)
    random.seed(args.seed)

    print("=" * 60)
    print("Unified Evaluation Script (Optimized Pipeline)")
    print("=" * 60)
    print(f"Cycle: {args.cycle}")
    print(f"Mode: {args.mode}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Base Model: {base_model_id}")
    print(f"FT Model: {ft_model_path} ({ft_mode})")
    print(f"Eval file: {eval_file}")
    print(f"Output: {output_dir}")

    if args.fresh and output_dir.exists():
        import shutil

        shutil.rmtree(output_dir)
        print(f"Cleared output directory: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Check for existing checkpoints to resume
    base_ckpt = output_dir / "base_checkpoint.json"
    ft_ckpt = output_dir / "ft_checkpoint.json"
    resume_base = []
    resume_ft = []

    if base_ckpt.exists():
        try:
            with open(base_ckpt, "r") as f:
                resume_base = json.load(f)
            print(f"Resuming BASE from checkpoint: {len(resume_base)} items")
        except Exception as e:
            print(f"Warning: Could not load BASE checkpoint: {e}")

    if ft_ckpt.exists():
        try:
            with open(ft_ckpt, "r") as f:
                resume_ft = json.load(f)
            print(f"Resuming FT from checkpoint: {len(resume_ft)} items")
        except Exception as e:
            print(f"Warning: Could not load FT checkpoint: {e}")

    print("\n[1/5] Loading eval data...")
    eval_data = load_eval_data(eval_file)
    print(f"Loaded {len(eval_data)} examples")

    if args.mode in ["small", "test"]:
        eval_data = sample_per_category(eval_data, samples=args.test_samples)
        print(f"Small/Test mode: {len(eval_data)} samples from different categories")
    elif args.mode == "medium":
        if args.samples < len(eval_data):
            eval_data = sample_stratified(eval_data, samples=args.samples)
            print(f"Medium mode: {len(eval_data)} stratified samples")
    elif args.mode == "full":
        print(f"Full mode: {len(eval_data)} samples (all data)")

    categories = set(
        d.get("metadata", {}).get("category", "unknown") for d in eval_data
    )
    print(f"Categories: {len(categories)}")

    print("\n[2/5] Initializing scorers...")
    semantic_scorer = SemanticScorer()
    try:
        semantic_scorer.load_model()
        print("Semantic scorer loaded")
    except Exception as e:
        print(f"Warning: Semantic scorer unavailable: {e}")
        semantic_scorer = None

    print("\n[3/5] Evaluating base model...")
    base_evaluator = UnifiedEvaluator(
        base_model_id=base_model_id,
        adapter_path="",
        merged_model_path="",
        batch_size=args.batch_size,
    )

    base_checkpoint = output_dir / "base_checkpoint.json"
    base_results = evaluate_model(
        base_evaluator,
        eval_data,
        semantic_scorer,
        mode="base",
        resume_results=resume_base if resume_base else None,
        checkpoint_file=base_checkpoint,
    )

    base_path = output_dir / "base_results.json"
    save_results(base_results, base_path)

    # Explicit memory cleanup to fit within RAM constraints
    base_evaluator.model = None
    base_evaluator.tokenizer = None
    del base_evaluator
    gc.collect()
    mx.clear_cache()

    print("\n[4/5] Evaluating fine-tuned model...")
    ft_evaluator = UnifiedEvaluator(
        base_model_id=base_model_id,
        adapter_path="" if ft_mode == "merged" else ft_model_path,
        merged_model_path=ft_model_path if ft_mode == "merged" else "",
        batch_size=args.batch_size,
    )

    ft_checkpoint = output_dir / "ft_checkpoint.json"
    ft_results = evaluate_model(
        ft_evaluator,
        eval_data,
        semantic_scorer,
        mode="ft",
        resume_results=resume_ft if resume_ft else None,
        checkpoint_file=ft_checkpoint,
    )

    ft_path = output_dir / "ft_results.json"
    save_results(ft_results, ft_path)

    # Explicit memory cleanup to fit within RAM constraints
    ft_evaluator.model = None
    ft_evaluator.tokenizer = None
    del ft_evaluator
    gc.collect()
    mx.clear_cache()

    print("\n[5/5] Generating reports...")
    reporter = ReportGenerator(output_dir)

    report_path = reporter.generate_comparison_report(
        base_results, ft_results, len(eval_data)
    )

    chart_paths = reporter.generate_charts(base_results, ft_results)

    print("\n" + "=" * 60)
    print("Evaluation Complete")
    print("=" * 60)
    print(f"Base model samples: {len(base_results)}")
    print(f"FT model samples: {len(ft_results)}")
    print(f"Report: {report_path}")
    if chart_paths:
        print("Charts:")
        for cp in chart_paths:
            print(f"  - {cp}")
    print("=" * 60)


if __name__ == "__main__":
    main()
