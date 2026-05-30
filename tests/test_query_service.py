from __future__ import annotations

import asyncio


class FakeConversationStore:
    def __init__(self) -> None:
        self.sessions: list[tuple[str, str | None, str | None]] = []
        self.messages: list[tuple[str, str, str, str, int, int]] = []
        self.touched: list[tuple[str, str]] = []

    def upsert_session(self, user_id: str, session_id: str | None, title: str | None = None) -> str:
        self.sessions.append((user_id, session_id, title))
        return session_id or "session-1"

    def load_recent_messages(self, session_id: str, limit: int = 8):
        return []

    def append_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        self.messages.append((user_id, session_id, role, content, input_tokens, output_tokens))

    def touch_session(self, user_id: str, session_id: str) -> None:
        self.touched.append((user_id, session_id))


class FakeQuotaStore:
    def __init__(self) -> None:
        self.ensure_calls: list[tuple[str, int]] = []
        self.consume_calls: list[tuple[str, int]] = []

    def ensure_quota(self, user_id: str, estimated_tokens: int) -> None:
        self.ensure_calls.append((user_id, estimated_tokens))

    def consume(self, user_id: str, tokens: int) -> None:
        self.consume_calls.append((user_id, tokens))


def test_query_service_persists_session_and_messages(monkeypatch):
    from compass.services.query import QueryService

    monkeypatch.setattr("compass.services.query.check_input", lambda query: None)
    monkeypatch.setattr("compass.services.query.check_output", lambda answer: None)
    monkeypatch.setattr("compass.services.query.expand_query", lambda query: [query])
    monkeypatch.setattr("compass.services.query.retrieve", lambda queries, top_k: ["chunk-1"])

    def fake_generate(query: str, context_chunks: list[str], conversation_history: str | None = None):
        from compass.infrastructure.bedrock_generator import GenerationResult

        assert conversation_history is None
        return GenerationResult(answer=f"echo:{query}", input_tokens=3, output_tokens=5)

    monkeypatch.setattr("compass.services.query.generate", fake_generate)

    store = FakeConversationStore()
    quota = FakeQuotaStore()
    service = QueryService(conversation_store=store, quota_store=quota)

    result = asyncio.run(service.execute("hola", user_id="user-1"))

    assert result.answer == "echo:hola"
    assert result.session_id == "session-1"
    assert store.sessions[0][0] == "user-1"
    assert store.messages[0][2] == "user"
    assert store.messages[1][2] == "assistant"
    assert store.touched == [("user-1", "session-1")]
    assert quota.ensure_calls[0][0] == "user-1"
    assert quota.consume_calls == [("user-1", 8)]
