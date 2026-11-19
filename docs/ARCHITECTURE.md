# Arquitetura funcional — Olist Intelligent Reviews

## Escopo

A Fase 2 definiu quatro agentes prioritários: Atendimento ao Cliente, Análise de Reviews, Logística e Previsão de Atrasos, e Churn e Fidelização. Para a Fase 3, o protótipo implementa somente o Agente de Análise de Reviews, preservando os outros três no roadmap.

## Componentes

1. Interface web em Gradio: entrada manual, upload de CSV/ZIP, análise individual, análise em lote, visão executiva e validação.
2. Camada de dados: leitura do CSV de avaliações; relacionamento opcional com Orders, Order_Items, Products e Sellers por order_id, product_id e seller_id.
3. Motor local: classificação explícita de sentimento, tema e severidade; detecção de divergência nota-texto; recomendação e encaminhamento.
4. Integração generativa opcional: OpenRouter, acionada manualmente para uma avaliação individual. Não é necessária para executar o fluxo básico.
5. Saídas: tabela estruturada, relatório executivo e CSV para auditoria.

## Fluxo operacional

Entrada da avaliação ou lote → validação → enriquecimento opcional → interpretação da nota e do comentário → classificação → severidade → recomendação → revisão humana quando crítica → saída estruturada.

## Entradas e saídas

| Elemento | Campos / conteúdo |
|---|---|
| Avaliações | review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date |
| Contexto opcional | status e datas do pedido; seller; produto; categoria |
| Saídas | sentimento, tema, severidade, evidência, recomendação, área responsável, divergência, necessidade de revisão humana |

## Limites de autonomia

O agente pode classificar, resumir, priorizar e recomendar. Não pode determinar culpa, confirmar fraude, aplicar penalidade a seller, autorizar reembolso, cancelar pedido ou alterar promessa de entrega. Alegações de fraude, autenticidade ou segurança exigem apuração humana.

## Separação entre regras e LLM

O motor local garante execução reproduzível sem rede ou API key. A LLM é opcional e atua como segunda opinião. A saída generativa não substitui evidência, controles nem revisão humana.
