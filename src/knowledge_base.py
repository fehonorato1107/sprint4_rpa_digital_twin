"""
knowledge_base.py — Base de conhecimento técnico do ativo (Sprint 4).
Alimenta o motor de decisão e o módulo RAG com procedimentos
corretivos/preventivos por tipo de anomalia.
"""
import json

from config import KB_PATH


# Seed da base de conhecimento (também persistida em data/knowledge_base.json)
KB_SEED = [
    {
        "tipo_anomalia": "alta_temperatura",
        "descricao": "Temperatura acima do limiar operacional",
        "causa_provavel": "Ventilação obstruída, sobrecarga ou rolamento desgastado",
        "severidade": "alerta",
        "procedimento_corretivo": "Verificar sistema de ventilação, reduzir carga e inspecionar rolamentos.",
        "procedimento_preventivo": "Limpeza periódica das aletas e monitoramento de carga.",
    },
    {
        "tipo_anomalia": "alta_vibracao",
        "descricao": "Vibração acima do limiar operacional",
        "causa_provavel": "Desalinhamento, desbalanceamento ou folga mecânica",
        "severidade": "alerta",
        "procedimento_corretivo": "Realizar alinhamento e balanceamento do rotor; verificar fixação da base.",
        "procedimento_preventivo": "Inspeção de alinhamento e balanceamento a cada ciclo programado.",
    },
    {
        "tipo_anomalia": "sobrecarga",
        "descricao": "Corrente acima do nominal",
        "causa_provavel": "Excesso de carga mecânica ou travamento do eixo",
        "severidade": "critico",
        "procedimento_corretivo": "Reduzir carga imediatamente e inspecionar acoplamento/eixo.",
        "procedimento_preventivo": "Dimensionamento de carga e proteção por relé de sobrecarga.",
    },
    {
        "tipo_anomalia": "subtensao",
        "descricao": "Tensão abaixo do nominal",
        "causa_provavel": "Falha na rede elétrica ou queda de fase",
        "severidade": "critico",
        "procedimento_corretivo": "Verificar alimentação e disjuntores; acionar equipe elétrica.",
        "procedimento_preventivo": "Monitoramento de qualidade de energia e proteções de fase.",
    },
    {
        "tipo_anomalia": "baixa_rotacao",
        "descricao": "Rotação abaixo do nominal",
        "causa_provavel": "Sobrecarga ou escorregamento excessivo",
        "severidade": "alerta",
        "procedimento_corretivo": "Avaliar carga aplicada e condição do rotor.",
        "procedimento_preventivo": "Acompanhamento de curva de carga e rotação.",
    },
]


class KnowledgeBase:
    """Carrega e consulta a base de conhecimento técnico."""

    def __init__(self, path=KB_PATH):
        self.path = path
        self._entries = self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Garante a criação do arquivo seed como evidência
            self._save(KB_SEED)
            return list(KB_SEED)

    def _save(self, entries):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def get(self, tipo_anomalia):
        """Retorna a entrada da base para um tipo de anomalia (ou None)."""
        for entry in self._entries:
            if entry["tipo_anomalia"] == tipo_anomalia:
                return entry
        return None

    def all_entries(self):
        return list(self._entries)