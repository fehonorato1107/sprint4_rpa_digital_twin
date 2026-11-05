"""
rpa_integrated.py — Pipeline RPA end-to-end (Sprint 4).
Orquestra, em loop autônomo com Try/Catch, todas as camadas das sprints
anteriores + a camada de suporte operacional:

  sensores → normalização → regras → persistência → decisão → evento → RAG

Cada ciclo é registrado em log estruturado (logs/execution.log) como
evidência de execução de ponta a ponta.
"""
import logging
import time
import traceback

import config
from database import DatabaseManager
from sensors import SensorSimulator
from knowledge_base import KnowledgeBase
from decision_engine import DecisionEngine
from event_lifecycle import EventLifecycle
from rag_exporter import RAGExporter


# --- Log estruturado (evidência de execução) ---
config.LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("rpa_integrated")


def normalizar(valor, minimo, maximo):
    """Normaliza um valor bruto para a escala 0–1 (Sprint 1)."""
    if maximo == minimo:
        return 0.0
    return max(0.0, min(1.0, (valor - minimo) / (maximo - minimo)))


def avaliar_status(temp_norm, vibra_norm):
    """Define o estado de saúde do motor a partir dos limiares (Sprint 3)."""
    if temp_norm >= config.CRITICO_TEMP_NORM or vibra_norm >= config.CRITICO_VIBRA_NORM:
        return config.STATUS_CRITICO
    if temp_norm >= config.ALERTA_TEMP_NORM or vibra_norm >= config.ALERTA_VIBRA_NORM:
        return config.STATUS_ALERTA
    return config.STATUS_OK


def processar_ciclo(db, sensor, engine, lifecycle, ativo_id):
    """Executa um ciclo completo de captura → decisão → persistência."""
    # 1. Captura (Sprint 1)
    leitura = sensor.read()

    # 2. Normalização (Sprint 1)
    temp_norm = normalizar(leitura["temp_bruta"], config.TEMP_MIN, config.TEMP_MAX)
    vibra_norm = normalizar(leitura["vibra_bruta"], config.VIBRA_MIN, config.VIBRA_MAX)

    # 3. Avaliação de status (Sprint 3)
    status = avaliar_status(temp_norm, vibra_norm)

    # 4. Persistência da leitura (Sprints 1/2/3)
    db.insert_leitura(
        {
            "timestamp": leitura["timestamp"],
            "ativo_id": ativo_id,
            "temp_bruta": leitura["temp_bruta"],
            "vibra_bruta": leitura["vibra_bruta"],
            "tensao": leitura["tensao"],
            "corrente": leitura["corrente"],
            "rotacao": leitura["rotacao"],
            "temp_norm": round(temp_norm, 3),
            "vibra_norm": round(vibra_norm, 3),
            "status": status,
        }
    )

    # 5. Sincronização do status do ativo em tempo real (Pilar 1)
    db.update_status_ativo(ativo_id, status)

    # 6. Detecção de anomalia + decisão (Pilar 2)
    tipo, severidade = engine.classificar_anomalia(
        temp_norm, vibra_norm, leitura["tensao"], leitura["corrente"]
    )

    if tipo:
        recomendacao = engine.recomendar(tipo)
        rec = recomendacao["recomendacao"] if recomendacao else "Inspeção manual."
        proc = recomendacao["procedimento"] if recomendacao else None
        evento_id, novo = lifecycle.abrir(ativo_id, tipo, severidade, rec, proc)
        if novo:
            log.info(
                "ALERTA | ativo=%s | anomalia=%s | severidade=%s | evento=%s | recomendacao=%s",
                ativo_id, tipo, severidade, evento_id, rec,
            )
        else:
            log.info("Evento %s já em andamento para o ativo %s", evento_id, ativo_id)
    else:
        # Status OK: encerra evento aberto, se houver (rastreabilidade)
        evento_aberto = db.evento_aberto_para_ativo(ativo_id)
        if evento_aberto:
            lifecycle.resolver(evento_aberto["id"], "Condição normalizada automaticamente.")
            log.info("RESOLVIDO | evento=%s | ativo=%s", evento_aberto["id"], ativo_id)

    return status, tipo


def main():
    """Ponto de entrada do RPA integrado."""
    log.info("=== Início do pipeline RPA integrado (Sprint 4) ===")

    db = DatabaseManager()
    sensor = SensorSimulator(seed=42)
    kb = KnowledgeBase()
    engine = DecisionEngine(kb)
    lifecycle = EventLifecycle(db)
    rag = RAGExporter(db, kb)

    # Cadastro do ativo (Sprint 2)
    ativo_id = db.upsert_ativo(
        tag="MOT-W22-001",
        localizacao="Linha de Produção A",
        tipo="Motor Elétrico W22",
        status=config.STATUS_OK,
    )
    log.info("Ativo registrado: MOT-W22-001 (id=%s)", ativo_id)

    ciclos = 0
    try:
        while config.MAX_CICLOS == 0 or ciclos < config.MAX_CICLOS:
            try:
                status, tipo = processar_ciclo(db, sensor, engine, lifecycle, ativo_id)
                ciclos += 1
                log.info(
                    "CICLO %s | status=%s | anomalia=%s",
                    ciclos, status, tipo or "nenhuma",
                )

                # Exportação RAG a cada 10 ciclos (Pilar 2)
                if ciclos % 10 == 0:
                    rag.export()
                    log.info("Contexto RAG exportado para %s", config.RAG_PATH)

                time.sleep(config.CICLO_SEGUNDOS)

            except Exception as exc:
                # Tratamento de exceção por ciclo: o RPA não morre (resiliência)
                log.error("Falha no ciclo %s: %s", ciclos + 1, exc)
                log.debug(traceback.format_exc())
                time.sleep(config.CICLO_SEGUNDOS)

    except KeyboardInterrupt:
        log.info("Execução interrompida pelo usuário.")

    finally:
        # Exportação final do contexto RAG (evidência de ponta a ponta)
        try:
            rag.export()
            log.info("Contexto RAG final exportado.")
        except Exception as exc:
            log.error("Falha na exportação final do RAG: %s", exc)

        log.info("=== Fim do pipeline RPA integrado ===")


if __name__ == "__main__":
    main()