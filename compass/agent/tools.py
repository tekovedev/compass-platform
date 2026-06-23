"""Strands tools for the Tránsito Seguro agent.

The Bedrock Knowledge Base retrieval is exposed here as a *tool* so the model
decides — per turn — whether it needs to consult the Código de Tránsito. A plain
greeting no longer forces a retrieval (and therefore no longer attaches sources).
"""

from __future__ import annotations

import logging
import threading

from strands import tool

logger = logging.getLogger(__name__)

from compass.infrastructure.bedrock_retriever import retrieve
from compass.infrastructure.query_expander import expand_query

# Captures the chunks retrieved during a single agent invocation, so the runtime
# entrypoint can surface them as `sources` only when the tool was actually used.
# A module-level list (not a contextvar) is used on purpose: Strands runs tools
# on worker threads, and contextvar writes there would not be visible to the
# calling thread. This assumes one invocation at a time per process — fine for an
# AgentCore runtime instance, which isolates sessions.
_lock = threading.Lock()
_retrieved_sources: list[str] = []


def reset_sources() -> None:
    """Start a fresh source-capture scope for one agent invocation."""
    with _lock:
        _retrieved_sources.clear()


def collected_sources() -> list[str]:
    """Return the chunks retrieved so far in the current invocation."""
    with _lock:
        return list(_retrieved_sources)


@tool
def buscar_codigo_transito(consulta: str) -> str:
    """Busca artículos relevantes del Código de Tránsito de Bolivia.

    Úsala cuando el usuario haga una pregunta legal concreta y específica sobre
    tránsito en Bolivia. No la uses para saludos, agradecimientos ni charla casual.

    Args:
        consulta: La pregunta o tema legal a buscar en el Código de Tránsito.

    Returns:
        Los fragmentos legales relevantes, separados por '---'.
    """
    logger.info("[TOOL] buscar_codigo_transito | consulta=%r", consulta)
    chunks = retrieve([consulta], top_k=5)
    logger.info("[TOOL] buscar_codigo_transito | retrieved %d chunks", len(chunks))
    for i, chunk in enumerate(chunks, 1):
        logger.debug("[RAG] chunk %d/%d:\n%s", i, len(chunks), chunk)
    with _lock:
        _retrieved_sources.extend(chunks)
    if not chunks:
        return "No se encontraron artículos relevantes en el corpus actual."
    return "\n\n---\n\n".join(chunks)


@tool
def buscar_con_expansion(consulta: str) -> str:
    """Busca artículos del Código de Tránsito expandiendo la consulta en variantes semánticas.

    Úsala cuando la pregunta del usuario sea vaga, amplia, o abarque varios temas a la vez.
    Genera 2 consultas alternativas con Nova Lite y combina los resultados con RRF para
    mayor cobertura que una búsqueda simple.

    Args:
        consulta: La pregunta o tema legal a buscar, posiblemente vaga o multi-tema.

    Returns:
        Los fragmentos legales relevantes, separados por '---'.
    """
    logger.info("[TOOL] buscar_con_expansion | consulta=%r", consulta)
    queries = expand_query(consulta)
    logger.info("[TOOL] buscar_con_expansion | expanded queries=%s", queries)
    chunks = retrieve(queries, top_k=5)
    logger.info("[TOOL] buscar_con_expansion | retrieved %d chunks", len(chunks))
    for i, chunk in enumerate(chunks, 1):
        logger.debug("[RAG] chunk %d/%d:\n%s", i, len(chunks), chunk)
    with _lock:
        _retrieved_sources.extend(chunks)
    if not chunks:
        return "No se encontraron artículos relevantes en el corpus actual."
    return "\n\n---\n\n".join(chunks)
