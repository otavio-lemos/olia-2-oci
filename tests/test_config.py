import pytest
from rag.config import (
    load_rag_config,
    get_rag_config,
    get_agent_config,
    get_workflow_config,
)


def test_load_rag_config():
    config = load_rag_config("config/oci-copilot-agents.yaml")
    assert config["rag"]["default_strategy"] == "hybrid"
    assert config["rag"]["fusion"]["dense_weight"] == 0.7


def test_get_rag_config():
    config = get_rag_config()
    assert config["default_strategy"] == "hybrid"


def test_get_agent_config():
    config = get_agent_config("migracao")
    assert config["rag_strategy"] == "hybrid"
    assert "migration" in config["metadata_filters"]["domain"]


def test_get_workflow_config():
    config = get_workflow_config("migracao")
    assert config["entry_agent"] == "router"
    assert "pipeline" in config
