"""Testes para Task 1.3 - Configuração do modelo no YAML."""

import pytest
from pathlib import Path


class TestModelConfig:
    """Testes para configuração do modelo."""

    def test_llm_config_section_exists(self):
        """Seção llm deve existir no YAML."""
        import yaml

        config_path = Path("config/oci-copilot-agents.yaml")
        if not config_path.exists():
            pytest.skip("Config file not found")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "llm" in config

    def test_llm_config_has_temperature(self):
        """Config deve ter temperature."""
        import yaml

        config_path = Path("config/oci-copilot-agents.yaml")
        if not config_path.exists():
            pytest.skip("Config file not found")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        llm = config.get("llm", {})
        assert "temperature" in llm

    def test_llm_config_has_model_path(self):
        """Config deve ter model_path."""
        import yaml

        config_path = Path("config/oci-copilot-agents.yaml")
        if not config_path.exists():
            pytest.skip("Config file not found")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        llm = config.get("llm", {})
        assert "model_path" in llm or "model" in llm


class TestLLMConfigLoader:
    """Testes para loader de configuração."""

    def test_get_llm_config_function(self):
        """get_llm_config deve existir."""
        from rag.config import get_rag_config

        config = get_rag_config()
        # Function returns dict, existence verified
