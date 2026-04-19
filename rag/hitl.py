"""HITL - Human-in-the-Loop para comandos destrutivos."""

from typing import List, Pattern
import re


DESTRUCTIVE_PATTERNS: List[Pattern] = [
    re.compile(r"terminate|delete|remove|drop|destroy", re.IGNORECASE),
]

DESTRUCTIVE_KEYWORDS = [
    "terminate",
    "delete",
    "remove",
    "drop",
    "destroy",
    "truncate",
    "cascade",
]

READ_ONLY_KEYWORDS = [
    "list",
    "get",
    "describe",
    "show",
    "ls",
    "cat",
    "head",
    "tail",
    "inspect",
]


class HITLChecker:
    """Verificador de comandos que requerem aprovação humana."""

    def __init__(self):
        self.destructive_patterns = DESTRUCTIVE_PATTERNS

    def is_destructive(self, command: str) -> bool:
        """Verifica se comando é destrutivo."""
        cmd_lower = command.lower()

        # Skip if it's read-only
        if any(kw in cmd_lower for kw in READ_ONLY_KEYWORDS):
            return False

        # Check for destructive keywords
        for keyword in DESTRUCTIVE_KEYWORDS:
            if keyword in cmd_lower:
                return True

        # Check patterns
        for pattern in self.destructive_patterns:
            if pattern.search(command):
                return True

        return False

    def requires_approval(self, command: str) -> bool:
        """Verifica se comando requer aprovação humana."""
        return self.is_destructive(command)

    def get_approval_message(self, command: str) -> str:
        """Retorna mensagem de aprovação."""
        return (
            f"⚠️ Comando potencialmente destrutivo detectado:\n\n"
            f"`{command}`\n\n"
            f"Deseja continuar? (sim/não)"
        )


def create_hitl_checker() -> HITLChecker:
    """Factory para criar HITLChecker."""
    return HITLChecker()
