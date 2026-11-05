"""
sensors.py — Camada de Extração (Sprint 1).
Simula os sensores IoT do motor W22 gerando leituras brutas contínuas.
"""
import random
from datetime import datetime


class SensorSimulator:
    """Gera leituras brutas de temperatura, vibração, tensão, corrente e rotação."""

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

    def read(self):
        """Retorna um dicionário com uma leitura bruta simulada."""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temp_bruta": round(random.uniform(25.0, 100.0), 4),
            "vibra_bruta": round(random.uniform(0.5, 9.5), 4),
            "tensao": round(random.uniform(200.0, 240.0), 2),
            "corrente": round(random.uniform(5.0, 40.0), 2),
            "rotacao": round(random.uniform(1500.0, 1800.0), 2),
        }