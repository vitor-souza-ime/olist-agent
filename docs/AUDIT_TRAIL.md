# Trilha de auditoria — Olist Intelligent Reviews

## Identificação

- Projeto: Olist Intelligent Marketplace.
- Entrega: Tech Challenge — Fase 3.
- Agente: Olist Intelligent Reviews.
- Repositório: https://github.com/vitor-souza-ime/olist-agent.

## Fontes

1. POSTECH — Tech Challenge — Fase 3.pdf, fornecido pelo usuário.
2. Relatório da Fase 2 — Tech_Challenge_Fase2_Olist_Agentes_IA(1).docx.
3. Olist, Brazilian E-Commerce Public Dataset by Olist, Kaggle (2018): https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

## Integridade do arquivo analisado

- Nome recebido: archive.zip.
- SHA-256: 967e41e04fc306fe604e2a693f488995a8b41e5047418f8a5c8e4abd6deca784.
- Linhas originais de reviews: 99.224.
- review_id únicos: 98.410.
- Linhas excedentes removidas: 814.
- Licença na fonte: CC BY-NC-SA 4.0.

## Rastreabilidade

| Requisito | Evidência |
|---|---|
| Evolução da Fase 2 | Relatório executivo consolidado |
| Protótipo funcional | app.py e app_real.py |
| Objetivo e fluxo | docs/AGENT_REAL.md e docs/ARCHITECTURE.md |
| Base de conhecimento/contexto | docs/DATA_ANALYSIS_REAL.md e data/dataset_manifest.json |
| Exemplos reais | IDs de reviews documentados no relatório e no roteiro |
| Avaliação do protótipo | docs/TEST_RESULTS.md |
| Limitações e próximos passos | Relatório executivo |
| Vídeo de até 5 minutos | docs/DEMO_SCRIPT.md; link pendente até gravação |

## Governança

- Não versionar API keys.
- Não concluir fraude, falsificação, defeito ou culpa de seller somente com review.
- Não executar reembolsos, cancelamentos ou penalidades.
- Revisar alegações críticas e casos ambíguos por pessoas responsáveis.
- O ZIP original não é versionado no GitHub; agregados e manifesto são mantidos para auditoria.
