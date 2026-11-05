"""
decision_engine.py — Motor de decisão e troubleshooting (Sprint 4).
Cruza o alerta detectado com a base de conhecimento e devolve a
recomendação corretiva/preventiva mais adequada.
"""
import config


class DecisionEngine:
    """Classifica a anomalia e recomenda procedimentos a partir do baseline."""

    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def classificar_anomalia(self, temp_norm, vibra_norm, tensao, corrente):
        """
        Determina o tipo de anomalia e a severidade a partir das leituras
        normalizadas e das grandezas elétricas.
        Retorna (tipo_anomalia, severidade) ou (None, None) se tudo OK.
        """
        # Prioridade: crítico > alerta
        if corrente > 35.0:
            return "sobrecarga", "critico"
        if tensao < 205.0:
            return "subtensao", "critico"
        if temp_norm >= config.CRITICO_TEMP_NORM:
            return "alta_temperatura", "critico"
        if vibra_norm >= config.CRITICO_VIBRA_NORM:
            return "alta_vibracao", "critico"
        if temp_norm >= config.ALERTA_TEMP_NORM:
            return "alta_temperatura", "alerta"
        if vibra_norm >= config.ALERTA_VIBRA_NORM:
            return "alta_vibracao", "alerta"
        return None, None

    def recomendar(self, tipo_anomalia):
        """Retorna a recomendação (corretivo + preventivo) para a anomalia."""
        entry = self.kb.get(tipo_anomalia)
        if not entry:
            return None
        return {
            "recomendacao": entry["procedimento_corretivo"],
            "procedimento": entry["procedimento_preventivo"],
            "causa_provavel": entry["causa_provavel"],
        }