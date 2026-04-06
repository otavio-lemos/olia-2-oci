#!/usr/bin/env python3
"""Shared evaluation scoring functions for OCI Specialist LLM benchmark."""

import re
from typing import Dict, Any, List
from pathlib import Path
import json


def load_eval_data(filepath: Path) -> List[Dict[str, Any]]:
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def get_user_prompt(example: Dict[str, Any]) -> str:
    for msg in example.get("messages", []):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def get_reference_answer(example: Dict[str, Any]) -> str:
    for msg in example.get("messages", []):
        if msg.get("role") == "assistant":
            return msg.get("content", "")
    return ""


def score_technical_correctness(response: str, reference: str, category: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    if len(response) < 100:
        score -= 1.0
    real_cli_patterns = [
        r"oci\s+(compute|network|db|bv|os|ce|fn|kms|vault|iam|logging|monitoring|resource-manager|devops|container-instance|nosql|mysql|cloud-guard|waas|apm|stack-monitoring|file-storage|load-balancer|api-gateway)",
        r"oci_core_instance",
        r"oci_objectstorage_bucket",
        r"oci_database_autonomous_database",
        r"oci_containerengine_cluster",
        r"oci\.core\.ComputeClient",
        r"oci\.object_storage\.ObjectStorageClient",
        r"oci\.database\.DatabaseClient",
    ]
    fake_cli_patterns = [
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
    ]
    has_real = any(re.search(p, response) for p in real_cli_patterns)
    has_fake = any(re.search(p, response) for p in fake_cli_patterns)
    cross_cloud_patterns = [
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
    ]
    has_cross_cloud = any(re.search(p, response) for p in cross_cloud_patterns)
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
    if category in terraform_cats:
        if "terraform" in response.lower() and (
            "resource" in response.lower() or "provider" in response.lower()
        ):
            score += 0.5
        if "oci_" in response:
            score += 0.5
    if "Allow group" in response and "to" in response and "in compartment" in response:
        score += 0.5
    if "Doc:" in response or "docs.oracle.com" in response:
        score += 0.3
    return max(1.0, min(5.0, score))


def score_depth(response: str, reference: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    depth_indicators = [
        (r"\d+\.\s+", 0.3),
        (r"```", 0.5),
        (r"- ", 0.2),
        (r"\* ", 0.2),
        (r"best practice", 0.3),
        (r"recomenda[çc][aã]o", 0.2),
        (r"trade.?off", 0.3),
        (r"vantagem", 0.2),
        (r"desvantagem", 0.2),
        (r"risco", 0.3),
        (r"mitiga[çc][aã]o", 0.3),
        (r"pr[ée]-requisito", 0.2),
        (r"valida[çc][aã]o", 0.2),
    ]
    for pattern, points in depth_indicators:
        if re.search(pattern, response, re.IGNORECASE):
            score += points
    word_count = len(response.split())
    if word_count > 200:
        score += 0.5
    if word_count > 500:
        score += 0.5
    if word_count < 50:
        score -= 1.0
    return max(1.0, min(5.0, score))


def score_structure(response: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    has_numbered_list = bool(re.search(r"\d+\.\s+", response))
    has_bullet_list = bool(re.search(r"^[-*]\s+", response, re.MULTILINE))
    has_code_block = "```" in response
    has_sections = bool(re.search(r"#+\s+", response))
    has_table = "|" in response and "---" in response
    structural_elements = sum(
        [has_numbered_list, has_bullet_list, has_code_block, has_sections, has_table]
    )
    if structural_elements >= 3:
        score += 1.5
    elif structural_elements >= 2:
        score += 1.0
    elif structural_elements >= 1:
        score += 0.5
    if len(response.split("\n")) > 10:
        score += 0.3
    return max(1.0, min(5.0, score))


def score_hallucination(response: str) -> float:
    score = 5.0
    if not response or response.startswith("Error:"):
        return 1.0
    hallucination_patterns = [
        (r"oci\s+instances\s+", 1.5),
        (r"oci\s+storage\s+(?!gateway)", 1.5),
        (r"oci\s+connectivity\s+", 1.5),
        (r"oci\s+block\s+(?!volume)", 1.5),
        (r"oci\s+autonomous-json", 1.5),
        (r"oci\s+azure-storage", 1.5),
        (r"oci\s+onprem-storage", 1.5),
        (r"oci\s+observability\s+", 1.5),
        (r"oci\s+authentication\s+", 1.5),
        (r"oci\.Compute\.InstancesClient", 1.5),
        (r"oci\.Storage\.BlockClient", 1.5),
        (r"oci\.ConnectivityClient", 1.5),
        (r"oci_compute_instances", 1.5),
        (r"oci_storage_block", 1.5),
        (r"oci_connectivity", 1.5),
        (r"semidesenvolvimento", 1.0),
        (r"Carneval", 1.0),
        (r"Insurance", 0.5),
        (r"deletar", 0.3),
    ]
    cross_cloud_patterns = [
        (r"provider\s+[\"']?aws[\"']?", 2.0),
        (r"resource\s+[\"']?aws_", 2.0),
        (r"resource\s+[\"']?azurerm_", 2.0),
        (r"aws_instance", 2.0),
        (r"aws_lb", 2.0),
        (r"aws_vpc", 2.0),
        (r"aws_security_group", 2.0),
        (r"aws_s3", 2.0),
        (r"aws_iam", 2.0),
        (r"azurerm_network_security_group", 2.0),
        (r"azurerm_virtual_network", 2.0),
        (r"azurerm_subnet", 2.0),
        (r"azurerm_public_ip", 2.0),
        (r"EC2", 1.5),
        (r"CloudWatch", 1.0),
        (r"AWS Management Console", 1.5),
        (r"AWS Console", 1.0),
        (r"Amazon Web Services", 1.0),
        (r"Azure Portal", 1.0),
        (r"Azure Resource Manager", 1.0),
    ]
    for pattern, penalty in hallucination_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            score -= penalty
    for pattern, penalty in cross_cloud_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            score -= penalty
    fake_urls = [
        r"/Content/\w+/Con/\w+\.htm",
        r"/Content/\w+/-\w+\.htm",
    ]
    for pattern in fake_urls:
        if re.search(pattern, response):
            score -= 1.0
    return max(1.0, min(5.0, score))


def score_clarity(response: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    if len(response) < 50:
        score -= 1.5
    elif len(response) < 100:
        score -= 0.5
    if len(response) > 2000:
        score -= 0.3
    sentences = re.split(r"[.!?]+", response)
    avg_sentence_length = len(response.split()) / max(len(sentences), 1)
    if 10 <= avg_sentence_length <= 25:
        score += 0.5
    if re.search(
        r"\b(portanto|assim|consequentemente|dessa forma|em resumo)\b",
        response,
        re.IGNORECASE,
    ):
        score += 0.3
    if re.search(
        r"\b(exemplo|por exemplo|como segue|veja que)\b", response, re.IGNORECASE
    ):
        score += 0.3
    return max(1.0, min(5.0, score))


def evaluate_response(response: str, reference: str, category: str) -> Dict[str, Any]:
    scores = {
        "technical_correctness": score_technical_correctness(
            response, reference, category
        ),
        "depth": score_depth(response, reference),
        "structure": score_structure(response),
        "hallucination": score_hallucination(response),
        "clarity": score_clarity(response),
    }
    scores["overall"] = sum(scores.values()) / len(scores)
    return scores
