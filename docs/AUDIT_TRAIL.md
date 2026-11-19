# Trilha de auditoria

## Identificação

- Projeto: Olist Intelligent Marketplace.
- Entrega: Tech Challenge — Fase 3 (Experiment & Build).
- Protótipo: Olist Intelligent Reviews.
- Agente implementado: Agente de Análise de Reviews.
- Repositório: https://github.com/vitor-souza-ime/olist-agent

## Fontes de requisitos

1. POSTECH - Tech Challenge - Fase 3.pdf, enviado no contexto deste projeto em 19/11/2026.
2. Tech_Challenge_Fase2_Olist_Agentes_IA(1).docx, relatório da Fase 2 enviado no mesmo contexto.
3. Dataset público Brazilian E-Commerce Public Dataset by Olist, disponível em https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

## Rastreabilidade requisito → implementação

| Requisito da Fase 3 | Evidência no protótipo |
|---|---|
| Objetivo do agente | README.md, docs/ARCHITECTURE.md e interface. |
| Fluxo básico | docs/ARCHITECTURE.md e fluxo operacional. |
| Interação com usuário | Abas “Analisar avaliação” e “Análise em lote”. |
| Base de conhecimento/contexto | Esquema de order_reviews e enriquecimento opcional com Orders, Order_Items, Products e Sellers. |
| Exemplos de interação | docs/TEST_PLAN.md e aba “Validação e auditoria”. |
| Avaliação do protótipo | docs/TEST_RESULTS.md. |
| Benefícios, limitações e melhorias | Relatório executivo da Fase 3. |
| Vídeo executivo de até 5 minutos | Roteiro preparado em docs/DEMO_SCRIPT.md; gravação/link permanecem pendentes. |

## Integridade e limitações da evidência

A amostra de 100 avaliações citada em uma demonstração anterior não foi recuperada com registros individuais, identificadores e critérios de seleção auditáveis. Portanto, as frequências e estatísticas associadas àquela demonstração não são incorporadas como resultados confirmados. O arquivo data/demo_reviews.csv contém dez casos sintéticos, identificados pelo prefixo DEMO-, exclusivamente para demonstrar e testar o fluxo.

## Segurança e governança

- Nenhuma chave de API é versionada.
- A integração externa é opcional e manual.
- O protótipo não executa ações transacionais nem sanções.
- Casos críticos são encaminhados para validação humana.
- O CSV de demonstração não contém identificadores reais de clientes ou pedidos.
