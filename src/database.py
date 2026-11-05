"""
database.py — Camada de persistência desacoplada (Sprints 2/3).
Encapsula o SQLite com lock de thread para evitar concorrência
e garante a criação idempotente do schema.
"""
import sqlite3
import threading
from contextlib import contextmanager

import config


class DatabaseManager:
    """Gerencia conexão, schema e transações do banco digital_twin.db."""

    def __init__(self, db_path=config.DB_PATH):
        self.db_path = str(db_path)
        self._lock = threading.Lock()   # lock para operações concorrentes
        self._init_schema()

    @contextmanager
    def connection(self):
        """Fornece uma conexão com commit/rollback automáticos."""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self):
        """Cria as tabelas caso ainda não existam (idempotente)."""
        with self._lock, self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS ativos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag TEXT UNIQUE NOT NULL,
                    localizacao TEXT,
                    tipo TEXT,
                    status TEXT
                );

                CREATE TABLE IF NOT EXISTS leituras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ativo_id INTEGER NOT NULL,
                    temp_bruta REAL, vibra_bruta REAL,
                    tensao REAL, corrente REAL, rotacao REAL,
                    temp_norm REAL, vibra_norm REAL,
                    status TEXT,
                    FOREIGN KEY (ativo_id) REFERENCES ativos(id)
                );

                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ativo_id INTEGER NOT NULL,
                    tipo_anomalia TEXT,
                    severidade TEXT,
                    status TEXT NOT NULL,
                    recomendacao TEXT,
                    procedimento TEXT,
                    responsavel TEXT,
                    resolucao TEXT,
                    timestamp_resolucao TEXT,
                    FOREIGN KEY (ativo_id) REFERENCES ativos(id)
                );
                """
            )

    # --- Operações de leitura/escrita ---
    def upsert_ativo(self, tag, localizacao, tipo, status):
        with self._lock, self.connection() as conn:
            conn.execute(
                """INSERT INTO ativos (tag, localizacao, tipo, status)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(tag) DO UPDATE SET
                     localizacao=excluded.localizacao,
                     tipo=excluded.tipo,
                     status=excluded.status""",
                (tag, localizacao, tipo, status),
            )
            row = conn.execute(
                "SELECT id FROM ativos WHERE tag=?", (tag,)
            ).fetchone()
            return row["id"]

    def insert_leitura(self, leitura: dict):
        with self._lock, self.connection() as conn:
            conn.execute(
                """INSERT INTO leituras
                   (timestamp, ativo_id, temp_bruta, vibra_bruta, tensao,
                    corrente, rotacao, temp_norm, vibra_norm, status)
                   VALUES (:timestamp, :ativo_id, :temp_bruta, :vibra_bruta,
                           :tensao, :corrente, :rotacao, :temp_norm,
                           :vibra_norm, :status)""",
                leitura,
            )

    def insert_evento(self, evento: dict):
        with self._lock, self.connection() as conn:
            conn.execute(
                """INSERT INTO eventos
                   (timestamp, ativo_id, tipo_anomalia, severidade, status,
                    recomendacao, procedimento, responsavel, resolucao,
                    timestamp_resolucao)
                   VALUES (:timestamp, :ativo_id, :tipo_anomalia, :severidade,
                           :status, :recomendacao, :procedimento, :responsavel,
                           :resolucao, :timestamp_resolucao)""",
                evento,
            )

    def update_status_ativo(self, ativo_id, status):
        with self._lock, self.connection() as conn:
            conn.execute(
                "UPDATE ativos SET status=? WHERE id=?", (status, ativo_id)
            )

    def update_evento(self, evento_id, **campos):
        """Atualiza dinamicamente campos de um evento (fechamento/rastreabilidade)."""
        if not campos:
            return
        set_clause = ", ".join(f"{k}=?" for k in campos)
        valores = list(campos.values()) + [evento_id]
        with self._lock, self.connection() as conn:
            conn.execute(
                f"UPDATE eventos SET {set_clause} WHERE id=?", valores
            )

    def evento_aberto_para_ativo(self, ativo_id):
        with self._lock, self.connection() as conn:
            row = conn.execute(
                """SELECT * FROM eventos
                   WHERE ativo_id=? AND status IN ('aberto', 'em_diagnostico')
                   ORDER BY id DESC LIMIT 1""",
                (ativo_id,),
            ).fetchone()
            return dict(row) if row else None

    def ultimas_leituras(self, limite=100):
        with self._lock, self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM leituras ORDER BY id DESC LIMIT ?", (limite,)
            ).fetchall()
            return [dict(r) for r in rows]

    def ultimos_eventos(self, limite=100):
        with self._lock, self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM eventos ORDER BY id DESC LIMIT ?", (limite,)
            ).fetchall()
            return [dict(r) for r in rows]