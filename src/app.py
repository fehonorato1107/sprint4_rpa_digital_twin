"""
app.py — Interface operacional Streamlit (Sprints 2/3).
Reflete em tempo real o status dos ativos, leituras e eventos
sincronizados pelo RPA integrado.
"""
import pandas as pd
import streamlit as st

from database import DatabaseManager


def main():
    st.set_page_config(page_title="Digital Twin W22", layout="wide")
    st.title("🛠️ Digital Twin — Motor W22")

    db = DatabaseManager()

    st.header("Status dos Ativos")
    with db.connection() as conn:
        ativos = pd.read_sql("SELECT * FROM ativos", conn)
    st.dataframe(ativos, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Leituras Recentes")
        with db.connection() as conn:
            leituras = pd.read_sql(
                "SELECT * FROM leituras ORDER BY id DESC LIMIT 50", conn
            )
        st.dataframe(leituras, use_container_width=True)

    with col2:
        st.subheader("Eventos (Ciclo de Vida)")
        with db.connection() as conn:
            eventos = pd.read_sql(
                "SELECT * FROM eventos ORDER BY id DESC LIMIT 50", conn
            )
        st.dataframe(eventos, use_container_width=True)


if __name__ == "__main__":
    main()