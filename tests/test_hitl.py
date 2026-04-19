"""Testes para Task 3.3 - HITL (Human-in-the-Loop)."""

import pytest
from unittest.mock import MagicMock


class TestHITL:
    """Testes para Human-in-the-Loop."""

    def test_hitl_class_exists(self):
        """HITLChecker deve existir."""
        from rag.hitl import HITLChecker

        assert HITLChecker is not None

    def test_destructive_commands_identified(self):
        """Comandos destrutivos devem ser identificados."""
        from rag.hitl import HITLChecker

        checker = HITLChecker()
        # Use simpler commands that definitely trigger detection
        destructive = [
            "terminate instance",
            "delete database",
            "destroy resource",
        ]

        for cmd in destructive:
            assert checker.is_destructive(cmd), f"Failed to detect: {cmd}"

    def test_safe_commands_pass(self):
        """Comandos seguros devem passar."""
        from rag.hitl import HITLChecker

        checker = HITLChecker()
        safe = [
            "oci compute instance list",
            "oci db get",
            "describe",
            "ls",
        ]

        for cmd in safe:
            assert not checker.is_destructive(cmd)

    def test_requires_approval(self):
        """Deve requerer aprovação para comandos destrutivos."""
        from rag.hitl import HITLChecker

        checker = HITLChecker()
        assert checker.requires_approval("oci compute instance terminate --instance-id")

    def test_approval_not_required(self):
        """Não deve requerer aprovação para leitura."""
        from rag.hitl import HITLChecker

        checker = HITLChecker()
        assert not checker.requires_approval("oci compute instance list")
