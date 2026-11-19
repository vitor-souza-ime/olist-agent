# Arquitetura — Olist Intelligent Reviews

## Componentes

- app.py: ponto de entrada da aplicação.
- app_real.py: interface Gradio, carregamento do ZIP, análise agregada, consulta gerencial e análise individual.
- olist_agent/llm.py: segunda opinião opcional via OpenRouter para uma avaliação individual.
- tests/: testes automatizados.
- docs/: especificação, análise quantitativa, plano de demonstração e trilha de auditoria.

## Fluxo

ZIP do dataset Olist → validação e deduplicação por review_id → normalização textual → triagem lexical multirrótulo → cruzamento com Orders e categorias → indicadores → resposta gerencial / análise individual → recomendação e revisão humana quando necessário.

## Relacionamentos

- Order_Reviews.order_id → Orders.order_id.
- Orders.order_id → Order_Items.order_id.
- Order_Items.product_id → Products.product_id.
- Order_Items.seller_id → Sellers.seller_id.

Os itens de cada pedido são agregados antes da associação para evitar multiplicar reviews de pedidos com vários produtos.

## Camadas

1. Motor quantitativo/lexical local: contagens reproduzíveis, sem API.
2. Leitura contextual: interpretação explicável de uma avaliação individual, sem afirmar causa como fato.
3. Segunda opinião semântica opcional: OpenRouter, acionada pelo usuário, não usada para gerar métricas agregadas.
4. Revisão humana: alegações críticas, ambiguidades e casos sem padrão lexical.

## Limites

O protótipo não acessa sistemas transacionais, não executa reembolso ou cancelamento e não aplica penalidades a sellers. Severidade é uma triagem, não probabilidade calibrada.
