"""Testes para Task 2.4 - Cross-Encoder re-ranking."""

import pytest
from unittest.mock import MagicMock, patch


class TestCrossEncoderReranker:
    """Testes para Cross-Encoder integração existente."""

    def test_config_yaml_has_reranking(self):
        """Config YAML deve ter re_ranking configurado."""
        import yaml
        from pathlib import Path

        config_path = Path("config/oci-copilot-agents.yaml")
        if not config_path.exists():
            pytest.skip("Config not found")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        rag_config = config.get("rag", {})
        assert "re_ranking" in rag_config

    def test_yaml_reranking_enabled(self):
        """re_ranking deve estar enabled no YAML."""
        import yaml
        from pathlib import Path

        config_path = Path("config/oci-copilot-agents.yaml")
        if not config_path.exists():
            pytest.skip("Config not found")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        reranking = config.get("rag", {}).get("re_ranking", {})
        assert "enabled" in reranking
        assert reranking["enabled"] is True


class TestRerankerIntegration:
    """Testes para configuração de re-ranking."""

    def test_yaml_has_reranking_config(self):
        """Config YAML deve ter re_ranking."""
        import yaml
        from pathlib import Path

        config_path = Path("config/oci-copilot-agents.yaml")
        if not config_path.exists():
            pytest.skip("Config not found")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        rag_config = config.get("rag", {})
        assert "re_ranking" in rag_config
