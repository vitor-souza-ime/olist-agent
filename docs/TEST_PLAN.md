# Plano de testes — agente com dados reais

## Casos automatizados

1. Pedido incompleto: classificar ausência de parte do pedido.
2. Entrega e devolução no mesmo comentário: detectar sinais simultâneos.
3. Qualidade com negação: reconhecer insatisfação em “não fiquei satisfeita”.
4. Alegação crítica: exigir revisão humana.
5. Divergência nota-texto: recomendar conferência humana.
6. Comentário vazio: não inferir causa.
7. Deduplicação por review_id: manter primeira ocorrência.
8. Pedido com vários itens: não multiplicar avaliações.
9. Validação do esquema: detectar IDs repetidos e comentários ausentes.
10. Análise agregada: calcular grupos e denominadores.
11. Resposta gerencial: utilizar os indicadores efetivamente calculados.

## Critério de aprovação

O caso é aprovado quando classificação, evidência, severidade, encaminhamento e tratamento de dados ausentes correspondem ao resultado esperado. A aprovação funcional não equivale a acurácia semântica generalizável.
