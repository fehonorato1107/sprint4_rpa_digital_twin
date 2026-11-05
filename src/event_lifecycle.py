"""
event_lifecycle.py — Ciclo de vida e rastreabilidade do evento (Sprint 4).
Gerencia a transição aberto → diagnóstico → resolvido/escalado,
garantindo governança sobre o ciclo de vida da falha.
"""
from datetime import datetime

import config


class EventLifecycle:
    """Controla abertura, diagnóstico e encerramento de eventos de falha."""

    def __init__(self, db):
        self.db = db

    def abrir(self, ativo_id, tipo_anomalia, severidade, recomendacao, procedimento):
        """Abre um novo evento (ou reaproveita um já aberto para o ativo)."""
        existente = self.db.evento_aberto_para_ativo(ativo_id)
        if existente:
            return existente["id"], False  # já existe evento em andamento

        evento = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ativo_id": ativo_id,
            "tipo_anomalia": tipo_anomalia,
            "severidade": severidade,
            "status": config.EVENTO_ABERTO,
            "recomendacao": recomendacao,
            "procedimento": procedimento,
            "responsavel": None,
            "resolucao": None,
            "timestamp_resolucao": None,
        }
        self.db.insert_evento(evento)
        novo = self.db.evento_aberto_para_ativo(ativo_id)
        return novo["id"], True

    def diagnosticar(self, evento_id, responsavel="Equipe de Manutenção"):
        """Move o evento para 'em_diagnostico' e atribui responsável."""
        self.db.update_evento(
            evento_id,
            status=config.EVENTO_DIAGNOSTICO,
            responsavel=responsavel,
        )

    def resolver(self, evento_id, resolucao):
        """Encerra o evento como 'resolvido' com a descrição da resolução."""
        self.db.update_evento(
            evento_id,
            status=config.EVENTO_RESOLVIDO,
            resolucao=resolucao,
            timestamp_resolucao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def escalar(self, evento_id, motivo):
        """Encaminha o evento como 'escalado' para nível superior."""
        self.db.update_evento(
            evento_id,
            status=config.EVENTO_ESCALADO,
            resolucao=f"Escalado: {motivo}",
            timestamp_resolucao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )