#!/usr/bin/env python3
"""
Content quality validator for OCI dataset.

Detects:
1. Generic/template responses (vague 4-step patterns)
2. Context pollution (compute params in non-compute categories)
3. Wrong CLI commands for category
4. Missing Portuguese diacritics
5. Structural repetition (same response template)
6. Missing or irrelevant content

Usage:
    python scripts/validate_content.py --input data/curated/
    python scripts/validate_content.py --input data/all_curated.jsonl
    python scripts/validate_content.py --input data/curated/ --filter --output data/curated_clean.jsonl
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter


# --- Detection patterns ---

# 1. Generic template responses - the "Para configurar X no OCI, siga estes passos" pattern
GENERIC_TEMPLATES = [
    r"Para configurar \w+ no OCI, siga estes passos",
    r"Para configurar \w+ no OCI, siga os seguintes passos",
    r"Acesse o Console OCI e navegue ate o servico correspondente",
    r"No Console, clique em 'Create' para o servico desejado",
    r"Configure os parametros conforme sua necessidade",
    r"Ajuste as configuracoes de rede e seguranca",
    r"Teste o acesso e conectividade",
    r"Verifique logs e metricas",
    r"Documente a configuracao",
]

# Generic 4-step pattern (all 4 steps present = definitely template)
FOUR_STEP_PATTERN = [
    r"Passo 1: Preparacao",
    r"Passo 2: Criacao",
    r"Passo 3: Configuracao",
    r"Passo 4: Validacao",
]

# Generic troubleshooting template
GENERIC_TROUBLESHOOTING = [
    r"Problema comum 1: Recurso nao inicia",
    r"Problema comum 2: Erro de permissao",
    r"Problema comum 3: Timeout de conexao",
    r"Verificar estado do recurso",
    r"Checklist de validacao",
]

# Generic best practices template
GENERIC_BEST_PRACTICES = [
    r"1\. Planejamento e Design",
    r"2\. Implementacao",
    r"3\. Seguranca",
    r"4\. Operacao",
    r"5\. Otimizacao",
    r"Defina claramente os requisitos de",
    r"Use Infrastructure as Code",
    r"Implemente tagging consistente",
]

# Generic security audit template (generic, not OCI-specific)
GENERIC_SECURITY_AUDIT = [
    r"Checklist de Seguranca",
    r"1\. Identity & Access Management",
    r"Policies com principio de menor privilegio",
    r"Grupos IAM organizados por funcao",
    r"MFA habilitado para todos os usuarios",
    r"Encryption em repouso",
    r"Encryption em transito",
]

# Generic integration pattern
GENERIC_INTEGRATION = [
    r"Servicos OCI que integram com",
    r"OCI Vault.*Encryption keys",
    r"OCI Monitoring.*Metricas e alertas",
    r"OCI Logging.*Logs estruturados",
]

# 2. Context pollution - compute-specific params in non-compute categories
COMPUTE_PARAMS = [
    r"shape=[A-Z]",
    r"\d+OCPUs",
    r"VM\.(Standard|GPU|DenseIO|Optimized)",
    r"BM\.(Standard|GPU)",
]

# Categories that should NOT have compute shape/OCPU params
NON_COMPUTE_CATEGORIES = {
    "database/",
    "networking/",
    "terraform/",
    "security/",
    "observability/",
    "devops/",
    "migration/",
    "serverless/",
    "load-balancing/",
    "container/",
}

# 3. Wrong CLI commands for category
# terraform questions should NOT have oci compute/commands
WRONG_CLI_MAP = {
    "terraform/": [
        r"oci compute instance launch",
        r"oci compute instance list",
        r"oci compute instance update",
        r"oci compute instance terminate",
        r"oci compute instance get",
        r"oci network vcn create",
        r"oci network vcn delete",
        r"oci db autonomous-database create",
        r"oci db autonomous-database delete",
    ],
    "database/": [
        r"oci compute instance launch",
        r"oci compute instance terminate",
    ],
    "networking/": [
        r"oci compute instance launch",
        r"oci compute instance terminate",
    ],
    "security/": [
        r"oci compute instance launch",
    ],
    "observability/": [
        r"oci compute instance launch",
    ],
    "devops/": [
        r"oci compute instance launch",
    ],
    "serverless/": [
        r"oci compute instance launch",
    ],
}

# 4. Missing diacritics - common Portuguese words that should have accents
MISSING_DIACRITICS_PATTERNS = [
    (r"\bconfiguracao\b", "configuração"),
    (r"\bpreparacao\b", "preparação"),
    (r"\bvalidacao\b", "validação"),
    (r"\bimplementacao\b", "implementação"),
    (r"\binstalacao\b", "instalação"),
    (r"\bpermissao\b", "permissão"),
    (r"\bpermissoes\b", "permissões"),
    (r"\bseguranca\b", "segurança"),
    (r"\bnao\b", "não"),
    (r"\bserie\b", "série"),
    (r"\bnumero\b", "número"),
    (r"\binstancias?\b", "instâncias"),
    (r"\bregion\b", "região"),
    (r"\bregioes\b", "regiões"),
    (r"\bacoes\b", "ações"),
    (r"\bcriacao\b", "criação"),
    (r"\bautomacao\b", "automação"),
    (r"\bautomatizado\b", "automatizado"),
    (r"\bdisponibilidade\b", "disponibilidade"),
    (r"\butilizacao\b", "utilização"),
    (r"\bmonitoramento\b", "monitoramento"),
    (r"\bmonitoracao\b", "monitoração"),
    (r"\bnotificacao\b", "notificação"),
    (r"\bautenticacao\b", "autenticação"),
    (r"\baplicacao\b", "aplicação"),
    (r"\baplicacoes\b", "aplicações"),
    (r"\bconexao\b", "conexão"),
    (r"\bconexoes\b", "conexões"),
    (r"\bprotecao\b", "proteção"),
    (r"\bcorrupcao\b", "corrupção"),
    (r"\bexecucao\b", "execução"),
    (r"\bcomunicacao\b", "comunicação"),
    (r"\binformacao\b", "informação"),
    (r"\binformacoes\b", "informações"),
    (r"\bdocumentacao\b", "documentação"),
    (r"\bavaliacao\b", "avaliação"),
    (r"\botimizacao\b", "otimização"),
    (r"\brazao\b", "razão"),
    (r"\bfuncao\b", "função"),
    (r"\bfuncoes\b", "funções"),
    (r"\boperacao\b", "operação"),
    (r"\boperacoes\b", "operações"),
    (r"\bproducao\b", "produção"),
    (r"\bsecao\b", "seção"),
    (r"\blicenca\b", "licença"),
    (r"\blicencas\b", "licenças"),
    (r"\bconsistencia\b", "consistência"),
    (r"\bexperiencia\b", "experiência"),
    (r"\bciencia\b", "ciência"),
    (r"\banciao\b", "anciāo"),
    (r"\bportugues\b", "português"),
    (r"\bingles\b", "inglês"),
    (r"\bespecifico\b", "específico"),
    (r"\bespecifica\b", "específica"),
    (r"\bunico\b", "único"),
    (r"\bunica\b", "única"),
    (r"\bpublico\b", "público"),
    (r"\bpublica\b", "pública"),
    (r"\bprivado\b", "privado"),
    (r"\bperiodo\b", "período"),
    (r"\bmetrica\b", "métrica"),
    (r"\bmetricas\b", "métricas"),
    (r"\banalise\b", "análise"),
    (r"\bgrafico\b", "gráfico"),
    (r"\bgraficos\b", "gráficos"),
    (r"\brelatorio\b", "relatório"),
    (r"\brelatorios\b", "relatórios"),
    (r"\bpais\b", "país"),
    (r"\blogo\b", "lógico"),
    (r"\blogico\b", "lógico"),
    (r"\blogica\b", "lógica"),
    (r"\bpratica\b", "prática"),
    (r"\bpraticas\b", "práticas"),
    (r"\bpolitica\b", "política"),
    (r"\bpoliticas\b", "políticas"),
    (r"\bhistorico\b", "histórico"),
    (r"\bcaracteristica\b", "característica"),
    (r"\bcaracteristicas\b", "características"),
    (r"\btecnologia\b", "tecnologia"),
    (r"\btecnologias\b", "tecnologias"),
    (r"\bvariavel\b", "variável"),
    (r"\bvariaveis\b", "variáveis"),
    (r"\bpossivel\b", "possível"),
    (r"\bimpossivel\b", "impossível"),
    (r"\bnivel\b", "nível"),
    (r"\bniveis\b", "níveis"),
    (r"\bproprio\b", "próprio"),
    (r"\bpropria\b", "própria"),
    (r"\bevidencia\b", "evidência"),
    (r"\bgerenciamento\b", "gerenciamento"),
    (r"\barmazenamento\b", "armazenamento"),
    (r"\bgerenciado\b", "gerenciado"),
    (r"\bgerenciada\b", "gerenciada"),
    (r"\bindice\b", "índice"),
    (r"\bindices\b", "índices"),
    (r"\bcontem\b", "contém"),
    (r"\balem\b", "além"),
    (r"\batribuido\b", "atribuído"),
    (r"\bconstrucao\b", "construção"),
    (r"\bselecao\b", "seleção"),
    (r"\bcolecao\b", "coleção"),
    (r"\bcolecoes\b", "coleções"),
    (r"\bopcoes\b", "opções"),
    (r"\bcondicoes\b", "condições"),
    (r"\btransicao\b", "transição"),
    (r"\bpos\b", "pós"),
    (r"\bpre\b", "pré"),
    (r"\bpre-requisito\b", "pré-requisito"),
    (r"\bpre-requisitos\b", "pré-requisitos"),
]


class ContentValidator:
    """Validates content quality of OCI dataset examples."""

    def __init__(self):
        self.issues = []
        self.stats = defaultdict(lambda: defaultdict(int))
        self.doc_urls = defaultdict(set)

    def validate_example(
        self, example: Dict[str, Any], line_num: int
    ) -> List[Dict[str, str]]:
        """Validate a single example and return list of issues found."""
        issues = []
        messages = example.get("messages", [])
        metadata = example.get("metadata", {})
        category = metadata.get("category", "unknown")

        # Get assistant response
        assistant_content = ""
        for msg in messages:
            if msg.get("role") == "assistant":
                assistant_content = msg.get("content", "")
                break

        if not assistant_content:
            issues.append(
                {
                    "line": line_num,
                    "category": category,
                    "type": "empty_response",
                    "severity": "critical",
                    "description": "Assistant response is empty",
                }
            )
            return issues

        # Check 1: Generic template responses
        generic_issues = self._check_generic_templates(assistant_content, category)
        for issue in generic_issues:
            issue["line"] = line_num
        issues.extend(generic_issues)

        # Check 2: Context pollution
        pollution_issues = self._check_context_pollution(
            example, assistant_content, category
        )
        for issue in pollution_issues:
            issue["line"] = line_num
        issues.extend(pollution_issues)

        # Check 3: Wrong CLI commands
        cli_issues = self._check_wrong_cli(assistant_content, category)
        for issue in cli_issues:
            issue["line"] = line_num
        issues.extend(cli_issues)

        # Check 4: Missing diacritics (count only, not per-example issue)
        diacritic_count = self._count_missing_diacritics(assistant_content)
        if diacritic_count > 0:
            self.stats[category]["diacritic_issues"] += diacritic_count

        # Check 5: Response too short (generic)
        word_count = len(assistant_content.split())
        if word_count < 30:
            issues.append(
                {
                    "line": line_num,
                    "category": category,
                    "type": "too_short",
                    "severity": "warning",
                    "description": f"Response too short: {word_count} words",
                }
            )

        # Check 6: Same doc URL for all (informational)
        doc_urls = re.findall(r"https://docs\.oracle\.com[^\s)]+", assistant_content)
        if doc_urls:
            self.doc_urls[category].add(doc_urls[0])

        return issues

    def _check_generic_templates(self, content: str, category: str) -> List[Dict]:
        """Detect generic template responses."""
        issues = []

        # Count how many generic phrases are present
        generic_matches = 0
        for pattern in GENERIC_TEMPLATES:
            if re.search(pattern, content, re.IGNORECASE):
                generic_matches += 1

        # Check 4-step pattern
        four_step_matches = 0
        for pattern in FOUR_STEP_PATTERN:
            if re.search(pattern, content, re.IGNORECASE):
                four_step_matches += 1

        # Check troubleshooting template
        troubleshooting_matches = 0
        for pattern in GENERIC_TROUBLESHOOTING:
            if re.search(pattern, content, re.IGNORECASE):
                troubleshooting_matches += 1

        # Check best practices template
        best_practices_matches = 0
        for pattern in GENERIC_BEST_PRACTICES:
            if re.search(pattern, content, re.IGNORECASE):
                best_practices_matches += 1

        # Check security audit template
        security_matches = 0
        for pattern in GENERIC_SECURITY_AUDIT:
            if re.search(pattern, content, re.IGNORECASE):
                security_matches += 1

        # Check integration pattern
        integration_matches = 0
        for pattern in GENERIC_INTEGRATION:
            if re.search(pattern, content, re.IGNORECASE):
                integration_matches += 1

        # Determine severity
        if four_step_matches >= 4:
            issues.append(
                {
                    "category": category,
                    "type": "generic_4step_template",
                    "severity": "critical",
                    "description": "Generic 4-step template detected (all 4 steps present)",
                }
            )
        elif generic_matches >= 5:
            issues.append(
                {
                    "category": category,
                    "type": "generic_template",
                    "severity": "critical",
                    "description": f"Generic template response ({generic_matches} generic phrases)",
                }
            )
        elif troubleshooting_matches >= 4:
            issues.append(
                {
                    "category": category,
                    "type": "generic_troubleshooting",
                    "severity": "critical",
                    "description": "Generic troubleshooting template (not category-specific)",
                }
            )
        elif best_practices_matches >= 6:
            issues.append(
                {
                    "category": category,
                    "type": "generic_best_practices",
                    "severity": "critical",
                    "description": "Generic best practices template (not category-specific)",
                }
            )
        elif security_matches >= 5:
            issues.append(
                {
                    "category": category,
                    "type": "generic_security_audit",
                    "severity": "critical",
                    "description": "Generic security audit checklist (not category-specific)",
                }
            )
        elif integration_matches >= 3:
            issues.append(
                {
                    "category": category,
                    "type": "generic_integration",
                    "severity": "critical",
                    "description": "Generic integration pattern (not category-specific)",
                }
            )

        return issues

    def _check_context_pollution(
        self, example: Dict, content: str, category: str
    ) -> List[Dict]:
        """Detect compute-specific params in non-compute categories."""
        issues = []

        # Check if category is non-compute
        is_non_compute = any(
            category.startswith(prefix) for prefix in NON_COMPUTE_CATEGORIES
        )

        if is_non_compute:
            # Check for compute params in the user message
            user_content = ""
            for msg in example.get("messages", []):
                if msg.get("role") == "user":
                    user_content = msg.get("content", "")
                    break

            compute_param_count = 0
            for pattern in COMPUTE_PARAMS:
                if re.search(pattern, user_content):
                    compute_param_count += 1

            if compute_param_count >= 2:
                issues.append(
                    {
                        "category": category,
                        "type": "context_pollution",
                        "severity": "warning",
                        "description": f"Compute-specific params in non-compute category ({compute_param_count} params found)",
                    }
                )

            # Also check if response mentions irrelevant shapes
            for pattern in COMPUTE_PARAMS:
                if re.search(pattern, content):
                    issues.append(
                        {
                            "category": category,
                            "type": "shape_in_response",
                            "severity": "warning",
                            "description": f"Compute shape/OCPU mentioned in {category} response",
                        }
                    )
                    break

        return issues

    def _check_wrong_cli(self, content: str, category: str) -> List[Dict]:
        """Detect wrong CLI commands for a category."""
        issues = []

        for cat_prefix, wrong_patterns in WRONG_CLI_MAP.items():
            if category.startswith(cat_prefix):
                for pattern in wrong_patterns:
                    if re.search(pattern, content):
                        issues.append(
                            {
                                "category": category,
                                "type": "wrong_cli",
                                "severity": "critical",
                                "description": f"Wrong CLI command for {category}: {pattern}",
                            }
                        )
                        break  # One issue per category match is enough

        return issues

    def _count_missing_diacritics(self, content: str) -> int:
        """Count missing diacritics in content."""
        count = 0
        for pattern, _ in MISSING_DIACRITICS_PATTERNS:
            count += len(re.findall(pattern, content, re.IGNORECASE))
        return count


def load_examples(input_path: Path) -> List[Dict[str, Any]]:
    """Load examples from JSONL file or directory."""
    examples = []

    if input_path.is_file() and input_path.suffix == ".jsonl":
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        examples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    elif input_path.is_dir():
        for json_file in sorted(input_path.rglob("*.jsonl")):
            with open(json_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            examples.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

    return examples


def generate_report(
    validator: ContentValidator, all_issues: List[Dict], total: int
) -> str:
    """Generate a quality report."""
    # Aggregate issues by type and category
    issue_counts = Counter()
    category_issues = defaultdict(lambda: Counter())
    severity_counts = Counter()

    for issue in all_issues:
        issue_counts[issue["type"]] += 1
        category_issues[issue["category"]][issue["type"]] += 1
        severity_counts[issue["severity"]] += 1

    # Calculate affected examples
    affected_lines = set()
    for issue in all_issues:
        affected_lines.add(issue["line"])

    # Diacritic stats
    total_diacritic_issues = sum(
        stats.get("diacritic_issues", 0) for stats in validator.stats.values()
    )

    report = f"""# Dataset Content Quality Report

**Total examples analyzed:** {total}
**Examples with issues:** {len(affected_lines)} ({len(affected_lines) / max(total, 1) * 100:.1f}%)
**Total issues found:** {len(all_issues)}

## Summary by Severity

| Severity | Count |
|----------|-------|
| Critical | {severity_counts.get("critical", 0)} |
| Warning | {severity_counts.get("warning", 0)} |

## Issue Types

| Issue Type | Count | Description |
|------------|-------|-------------|
"""

    type_descriptions = {
        "generic_4step_template": "Generic 4-step template (Passo 1-4)",
        "generic_template": "Generic template response",
        "generic_troubleshooting": "Generic troubleshooting template",
        "generic_best_practices": "Generic best practices template",
        "generic_security_audit": "Generic security audit checklist",
        "generic_integration": "Generic integration pattern",
        "context_pollution": "Compute params in non-compute category",
        "shape_in_response": "Compute shape mentioned in wrong category",
        "wrong_cli": "Wrong CLI command for category",
        "empty_response": "Empty assistant response",
        "too_short": "Response too short (<30 words)",
    }

    for issue_type, count in issue_counts.most_common():
        desc = type_descriptions.get(issue_type, issue_type)
        report += f"| {desc} | {count} |\n"

    report += f"\n## Diacritics\n\n"
    report += f"**Total missing diacritics:** {total_diacritic_issues}\n\n"

    report += f"\n## Issues by Category\n\n"
    report += "| Category | Total Issues | Critical | Warning |\n|----------|-------------|----------|---------|\n"

    for category in sorted(category_issues.keys()):
        cat_counts = category_issues[category]
        total_cat = sum(cat_counts.values())
        critical = sum(v for k, v in cat_counts.items() if "critical" in str(k))
        # Recalculate properly
        critical = 0
        warning = 0
        for issue in all_issues:
            if issue["category"] == category:
                if issue["severity"] == "critical":
                    critical += 1
                elif issue["severity"] == "warning":
                    warning += 1
        report += f"| {category} | {total_cat} | {critical} | {warning} |\n"

    report += f"\n## Top 20 Most Affected Examples\n\n"
    report += "| Line | Category | Issues |\n|------|----------|--------|\n"

    # Group issues by line
    line_issues = defaultdict(list)
    for issue in all_issues:
        line_issues[issue["line"]].append(issue)

    # Sort by number of issues per line
    sorted_lines = sorted(line_issues.items(), key=lambda x: len(x[1]), reverse=True)

    for line, issues in sorted_lines[:20]:
        issue_types = ", ".join(set(i["type"] for i in issues))
        categories = set(i["category"] for i in issues)
        report += f"| {line} | {', '.join(categories)} | {issue_types} |\n"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate content quality of OCI dataset"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="JSONL file or curated dir"
    )
    parser.add_argument(
        "--filter", action="store_true", help="Output only clean examples"
    )
    parser.add_argument("--output", "-o", help="Output file for filtered examples")
    parser.add_argument(
        "--report",
        "-r",
        default="outputs/benchmarks/content-quality-report.md",
        help="Output path for quality report",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    print(f"Loading examples from {input_path}...")
    examples = load_examples(input_path)
    print(f"Loaded {len(examples)} examples")

    validator = ContentValidator()
    all_issues = []
    clean_examples = []

    print("Validating content quality...")
    for i, example in enumerate(examples):
        issues = validator.validate_example(example, line_num=i)
        all_issues.extend(issues)

        if not issues:
            clean_examples.append(example)

        if (i + 1) % 1000 == 0:
            print(
                f"  Processed {i + 1}/{len(examples)} examples, {len(all_issues)} issues found so far"
            )

    print(f"\nValidation complete!")
    print(f"  Total examples: {len(examples)}")
    print(
        f"  Clean examples: {len(clean_examples)} ({len(clean_examples) / max(len(examples), 1) * 100:.1f}%)"
    )
    print(
        f"  Affected examples: {len(examples) - len(clean_examples)} ({(len(examples) - len(clean_examples)) / max(len(examples), 1) * 100:.1f}%)"
    )
    print(f"  Total issues: {len(all_issues)}")

    # Generate report
    report = generate_report(validator, all_issues, len(examples))
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    # Save filtered examples if requested
    if args.filter and args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for example in clean_examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
        print(f"Clean examples saved to {output_path} ({len(clean_examples)} examples)")

    # Print summary
    issue_counts = Counter(issue["type"] for issue in all_issues)
    print("\nIssue breakdown:")
    for issue_type, count in issue_counts.most_common():
        print(f"  {issue_type}: {count}")


if __name__ == "__main__":
    main()
