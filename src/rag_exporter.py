"""
rag_exporter.py — Disponibilização de dados para Assistente/RAG (Sprint 4).
Estrutura e exporta dados operacionais + histórico + base de conhecimento
em JSON para alimentar o módulo conversacional de diagnóstico.
"""
import json

from config import RAG_PATH


class RAGExporter:
    """Constrói e persiste o contexto estruturado consumível por um RAG."""

    def __init__(self, db, knowledge_base):
        self.db = db
        self.kb = knowledge_base

    def build_context(self):
        """Monta o documento de contexto com leituras, eventos e conhecimento."""
        return {
            "ativos": self._ativos(),
            "leituras_recentes": self.db.ultimas_leituras(limite=50),
            "eventos": self.db.ultimos_eventos(limite=50),
            "base_conhecimento": self.kb.all_entries(),
        }

    def _ativos(self):
        with self.db.connection() as conn:
            rows = conn.execute("SELECT * FROM ativos").fetchall()
            return [dict(r) for r in rows]

    def export(self):
        """Serializa o contexto em JSON (evidência + fonte para o RAG)."""
        contexto = self.build_context()
        RAG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RAG_PATH, "w", encoding="utf-8") as f:
            json.dump(contexto, f, ensure_ascii=False, indent=2, default=str)
        return RAG_PATH