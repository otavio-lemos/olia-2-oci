#!/usr/bin/env python3
"""Factual consistency checking for OCI responses."""

import re
import json
from typing import List, Dict, Any, Tuple


class FactualChecker:
    """Check factual accuracy of OCI responses against known patterns."""

    VALID_SHAPES = [
        r"VM\.Standard\.E[0-9]\.Flex",
        r"VM\.Standard\.A[0-9]\.Flex",
        r"VM\.Standard\.B[0-9]\.Flex",
        r"VM\.Standard\.E[0-9]\.Flex",
        r"BM\.Standard\.[A-Z0-9]+",
        r"GPU\.[A-Z0-9\.]+",
        r"VM\.Optimized3\.Flex",
    ]

    VALID_REGIONS = [
        "sa-saopaulo-1",
        "sa-vinhedo-1",
        "us-ashburn-1",
        "us-phoenix-1",
        "uk-london-1",
        "eu-frankfurt-1",
        "ap-tokyo-1",
        "ap-seoul-1",
        "ap-melbourne-1",
        "ca-toronto-1",
        "eu-amsterdam-1",
        "ap-osaka-1",
        "me-jeddah-1",
        "uk-cardiff-1",
        "il-jerusalem-1",
        "sa-saopaulo-2",
        "eu-zurich-1",
        "eu-marseille-1",
    ]

    VALID_CLI_COMMANDS = [
        r"oci\s+(compute|db|network|iam|object-storage|fs|lb|logging|logs|container|functions|apigateway|autonomous|audit|bloomberg)\s+\w+",
    ]

    FAKE_OCI_SERVICES = [
        r"oci\s+(quantum|ml\s+service|fabric|mesh|graph|datascience|ai\s+vision|ai\s+language)\s+\w+",
    ]

    CROSS_CLOUD_PATTERNS = [
        r"(aws_|azure_|gcp_|s3\.amazon|blob\.core\.windows|gs\.)",
        r"(ec2|rds|s3|lambda|azure-sql|bigquery)",
        r"(amazon\s+web\s+services|microsoft\s+azure|google\s+cloud)",
    ]

    def __init__(self):
        self.shape_pattern = re.compile("|".join(self.VALID_SHAPES), re.IGNORECASE)
        self.cli_pattern = re.compile("|".join(self.VALID_CLI_COMMANDS), re.IGNORECASE)
        self.fake_service_pattern = re.compile(
            "|".join(self.FAKE_OCI_SERVICES), re.IGNORECASE
        )
        self.cross_cloud_pattern = re.compile(
            "|".join(self.CROSS_CLOUD_PATTERNS), re.IGNORECASE
        )

    def check_shapes(self, text: str) -> Tuple[bool, List[str]]:
        """Validate shapes mentioned in text."""
        shapes = self.shape_pattern.findall(text)
        return len(shapes) > 0, shapes

    def check_regions(self, text: str) -> Tuple[bool, List[str]]:
        """Validate regions mentioned in text."""
        text_lower = text.lower()
        regions = [r for r in self.VALID_REGIONS if r in text_lower]
        return len(regions) > 0, regions

    def check_cli_commands(self, text: str) -> List[str]:
        """Extract and validate OCI CLI commands."""
        commands = self.cli_pattern.findall(text)
        return commands

    def check_response(self, text: str, category: str = "") -> Dict[str, Any]:
        """Full factual check of response."""
        shapes_ok, shapes = self.check_shapes(text)
        regions_ok, regions = self.check_regions(text)
        cli_commands = self.check_cli_commands(text)

        hallucinations = []

        if self.cross_cloud_pattern.search(text):
            hallucinations.append("cross_cloud_reference")

        if self.fake_service_pattern.search(text):
            hallucinations.append("fake_oci_service")

        score = 1.0
        if not shapes_ok:
            score -= 0.1
        if not regions_ok:
            score -= 0.05
        score -= len(hallucinations) * 0.2

        return {
            "shapes_valid": shapes_ok,
            "shapes_found": shapes,
            "regions_valid": regions_ok,
            "regions_found": regions,
            "cli_commands_found": cli_commands,
            "potential_hallucinations": hallucinations,
            "factuality_score": round(max(0.0, score), 2),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Factual consistency checker for OCI responses"
    )
    parser.add_argument("--text", required=True, help="Text to check")
    args = parser.parse_args()

    checker = FactualChecker()
    result = checker.check_response(args.text)

    print("=== Factual Consistency Check ===")
    print(f"Shapes Valid: {result['shapes_valid']}")
    print(f"Shapes Found: {result['shapes_found']}")
    print(f"Regions Valid: {result['regions_valid']}")
    print(f"Regions Found: {result['regions_found']}")
    print(f"CLI Commands: {result['cli_commands_found']}")
    print(f"Hallucinations: {result['potential_hallucinations']}")
    print(f"Factuality Score: {result['factuality_score']}/1.0")


if __name__ == "__main__":
    main()
