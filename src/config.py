"""
config.py — Constantes e configurações centrais do Digital Twin W22.
Centraliza limiares, caminhos e parâmetros para evitar valores mágicos
espalhados pelo código (critério: qualidade e organização).
"""
from pathlib import Path

# --- Caminhos ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "digital_twin.db"
KB_PATH = DATA_DIR / "knowledge_base.json"
RAG_PATH = DATA_DIR / "rag_context.json"
LOG_PATH = LOG_DIR / "execution.log"

# --- Parâmetros do RPA ---
CICLO_SEGUNDOS = 1.0          # cadência do loop autônomo (time.sleep)
MAX_CICLOS = 60               # limite de ciclos por execução (0 = infinito)

# --- Limiares de normalização (Sprint 1) ---
TEMP_MIN, TEMP_MAX = 20.0, 100.0     # faixa operacional de temperatura (°C)
VIBRA_MIN, VIBRA_MAX = 0.0, 10.0     # faixa operacional de vibração (mm/s)

# --- Limiares de alerta (Sprint 3 — baseline técnico) ---
ALERTA_TEMP_NORM = 0.75       # temperatura normalizada acima disso => alerta
ALERTA_VIBRA_NORM = 0.75      # vibração normalizada acima disso => alerta
CRITICO_TEMP_NORM = 0.90      # acima disso => crítico
CRITICO_VIBRA_NORM = 0.90

# --- Estados operacionais ---
STATUS_OK = "Operação Normal"
STATUS_ALERTA = "Alerta"
STATUS_CRITICO = "Crítico"

# --- Estados do ciclo de vida do evento (Sprint 4) ---
EVENTO_ABERTO = "aberto"
EVENTO_DIAGNOSTICO = "em_diagnostico"
EVENTO_RESOLVIDO = "resolvido"
EVENTO_ESCALADO = "escalado"