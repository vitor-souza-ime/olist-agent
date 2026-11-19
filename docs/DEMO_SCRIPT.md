# Roteiro de demonstração — até 5 minutos

## 0:00–0:30 — Abertura

Apresentar a evolução da Fase 2 para a Fase 3. Na Fase 2 foram definidos quatro agentes; nesta etapa, o Agente de Análise de Reviews foi prototipado.

## 0:30–1:05 — Dataset real

Mostrar o painel: 99.224 linhas originais, 98.410 review_id únicos após deduplicação, nota média 4,09 e 14,6% de avaliações com nota 1 ou 2.

## 1:05–2:00 — Pergunta ao agente

Na aba “Pergunte ao agente”, executar: “Quais são os três problemas mais importantes encontrados nas avaliações e o que a Olist deveria fazer?”

Mostrar:
1. Entrega e cumprimento do pedido: 3.970 comentários (36,6%).
2. Produto: qualidade, defeito ou divergência: 1.255 (11,6%).
3. Pós-venda: atendimento, devolução e pagamento: 852 (7,8%).

Explicar que os grupos são multirrótulo e os percentuais não são aditivos.

## 2:00–3:15 — Review real

Na aba “Analisar avaliação real”, selecionar review_id 96ab47052a57bbfbba3b48d4203cf1f3. Mostrar a nota 1, o relato de recebimento de metade do pedido apesar da nota fiscal indicar todos os itens, a classificação de pedido incompleto e a recomendação de conferir picking, packing, nota fiscal e comprovante.

## 3:15–4:05 — Relação com logística

Mostrar notas médias: 2,57 para pedidos atrasados e 4,30 para pedidos no prazo/antecipados. Mostrar também a proporção de notas 1–2: 54,1% versus 9,2%. Explicar que se trata de associação observacional.

## 4:05–4:40 — Limites e governança

A triagem lexical identificou padrões em 52,7% dos comentários negativos com texto. Os 47,3% restantes não foram classificados à força. Casos críticos e ambíguos exigem revisão humana. A segunda opinião generativa é opcional.

## 4:40–5:00 — Encerramento

Apresentar próximos passos: rotular amostra por especialistas, medir precisão e recall por tema, refinar taxonomia e integrar sinais aos demais agentes.

Link do vídeo: inserir após a gravação e publicação.
