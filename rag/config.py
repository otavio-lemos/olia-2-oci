"""Carrega configuração do YAML."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_rag_config(
    config_path: str = "config/oci-copilot-agents.yaml",
) -> Dict[str, Any]:
    """Carrega config do agente."""
    path = Path(config_path)
    if not path.exists():
        # Try relative to project root
        path = Path(__file__).parent.parent / config_path

    with open(path) as f:
        return yaml.safe_load(f)


def get_rag_config() -> Dict[str, Any]:
    """Retorna config RAG."""
    config = load_rag_config()
    return config.get("rag", {})


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Retorna config de um agente."""
    config = load_rag_config()
    return config.get("agents", {}).get(agent_name, {})


def get_workflow_config(workflow_name: str) -> Dict[str, Any]:
    """Retorna config de um workflow."""
    config = load_rag_config()
    return config.get("workflows", {}).get(workflow_name, {})
