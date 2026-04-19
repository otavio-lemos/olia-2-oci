"""Testes para Task 3.1 - Intent Classifier."""

import pytest
from unittest.mock import MagicMock, patch


class TestIntentClassifier:
    """Testes para IntentClassifier."""

    def test_classifier_exists(self):
        """IntentClassifier deve existir."""
        from rag.intent_router import IntentClassifier

        assert IntentClassifier is not None

    def test_classifier_has_classify_method(self):
        """Deve ter método classify."""
        from rag.intent_router import IntentClassifier

        classifier = IntentClassifier(embeddings=MagicMock())
        assert hasattr(classifier, "classify")

    @pytest.mark.asyncio
    async def test_classify_returns_intent(self):
        """classify deve retornar intent."""
        from rag.intent_router import IntentClassifier

        mock_embed = MagicMock()
        mock_embed.embed_query = MagicMock(return_value=[0.1] * 384)

        classifier = IntentClassifier(embeddings=mock_embed)
        result = await classifier.classify("create compute instance")

        assert result in [
            "migracao",
            "troubleshooting",
            "finops",
            "arquitetura",
            "descoberta",
            "execucao",
        ]


class TestIntentTypes:
    """Testes para tipos de intent."""

    def test_intent_list_covers_use_cases(self):
        """Lista de intents deve cobrir casos de uso."""
        from rag.intent_router import INTENT_TYPES

        expected = [
            "migracao",
            "troubleshooting",
            "finops",
            "arquitetura",
            "descoberta",
        ]
        for intent in expected:
            assert intent in INTENT_TYPES
