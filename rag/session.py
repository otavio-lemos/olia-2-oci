"""Session Manager - Gerenciamento de sessões e histórico."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import OrderedDict
from dataclasses import dataclass, field


@dataclass
class Session:
    """Dados de uma sessão."""

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    messages: list[dict] = field(default_factory=list)
    context_docs: list[Any] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)


class AgentFallback:
    """Lógica de fallback entre agentes."""

    def __init__(self):
        self.fallback_map = {
            "arquitetura": "descoberta",
            "migracao": "descoberta",
            "execucao": "arquitetura",
        }

    def get_fallback(self, failed_agent: str) -> str:
        """Retorna agente de fallback."""
        return self.fallback_map.get(failed_agent, "descoberta")


class SessionManager:
    """Gerenciador de sessões."""

    def __init__(self, max_sessions: int = 100, session_ttl: int = 30):
        self._sessions: dict[str, Session] = {}
        self._max_sessions = max_sessions
        self._session_ttl = timedelta(minutes=session_ttl)
        self._cache = OrderedDict()
        self.fallback = AgentFallback()

    def create_session(self) -> str:
        """Cria nova sessão."""
        # Cleanup old sessions
        self._cleanup_old_sessions()

        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id=session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Recupera sessão."""
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = datetime.now()
        return session

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Adiciona mensagem ao histórico."""
        session = self.get_session(session_id)
        if session:
            session.messages.append(
                {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def add_context(self, session_id: str, doc: Any) -> None:
        """Adiciona documento ao contexto."""
        session = self.get_session(session_id)
        if session:
            session.context_docs.append(doc)

    def get_history(self, session_id: str, max_messages: int = 10) -> list[dict]:
        """Retorna histórico de mensagens."""
        session = self.get_session(session_id)
        if not session:
            return []
        return session.messages[-max_messages:]

    def clear_session(self, session_id: str) -> None:
        """Limpa sessão."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _cleanup_old_sessions(self) -> None:
        """Remove sessões expiradas."""
        now = datetime.now()
        expired = [
            sid
            for sid, sess in self._sessions.items()
            if now - sess.last_activity > self._session_ttl
        ]
        for sid in expired:
            del self._sessions[sid]

        # Also enforce max sessions
        while len(self._sessions) > self._max_sessions:
            oldest = min(self._sessions.items(), key=lambda x: x[1].last_activity)
            del self._sessions[oldest[0]]


def create_session_manager() -> SessionManager:
    """Factory para criar SessionManager."""
    return SessionManager()
