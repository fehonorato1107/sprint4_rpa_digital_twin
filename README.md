# Sprint 4 — Integração da Solução e Suporte Operacional

Plataforma **Digital Twin** do motor elétrico W22. Esta sprint consolida as
automações das sprints anteriores em um **pipeline RPA end-to-end** e adiciona
a camada de **suporte operacional e troubleshooting**.

## O que foi integrado

| Sprint | Camada | Módulo |
|--------|--------|--------|
| 1 | Extração + Normalização | `sensors.py`, `rpa_integrated.py` |
| 2 | Ativo/TAG + Visualização | `database.py`, `app.py` |
| 3 | Regras + Baseline + Eventos | `decision_engine.py`, `database.py` |
| 4 | Suporte + RAG + Rastreabilidade | `knowledge_base.py`, `event_lifecycle.py`, `rag_exporter.py` |

## Como executar

```shell
pip install -r requirements.txt
python src/rpa_integrated.py      # pipeline RPA end-to-end
python -m streamlit run src/app.py  # dashboard (opcional)

